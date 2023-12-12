from functools import partial

import jax
import jax.numpy as jnp
from jax import Array, lax
from jax.typing import ArrayLike

from .distribution import Distribution


class TruncPowerLaw(Distribution):

    def __init__(self, alpha: ArrayLike, low: ArrayLike = 0, high: ArrayLike = 1, name: str = None) -> None:
        self._alpha = alpha
        self._low = low
        self._high = high
        self.check_params()
        self._beta = 1.0 + self._alpha
        self._logZ = self.logZ()
        super().__init__(name)

    def check_params(self) -> None:
        assert jnp.all(self._low > 0.0), "low must be greater than 0"
        assert jnp.all(self._high > self._low), "high must be greater than low"

    @partial(jax.jit, static_argnums=(0,))
    def logZ(self) -> ArrayLike:
        logZ_val = lax.cond(
            self._alpha == -1.0, lambda _: jnp.log(jnp.log(self._high) - jnp.log(self._low)), lambda beta: lax.cond(
                beta > 0.0,
                lambda b: jnp.log(jnp.power(self._high, b) - jnp.power(self._low, b)) - jnp.log(b),
                lambda b: jnp.log(jnp.power(self._low, b) - jnp.power(self._high, b)) - jnp.log(-b),
                self._beta,
            ), self._beta)
        return logZ_val

    @partial(jax.jit, static_argnums=(0,))
    def logpdf(self, x: ArrayLike) -> ArrayLike:
        logpdf_val = jnp.log(x) * self._alpha - self._logZ
        logpdf_val = jnp.where((x >= self._low) * (x <= self._high), logpdf_val, -jnp.inf)
        return logpdf_val

    @partial(jax.jit, static_argnums=(0,))
    def logcdf(self, x: ArrayLike) -> ArrayLike:
        logcdf_val = lax.cond(
            self._alpha == -1.0, lambda _: jnp.log(jnp.log(x) - jnp.log(self._low)), lambda beta: lax.cond(
                beta > 0.0,
                lambda b: jnp.log(jnp.power(x, b) - jnp.power(self._low, b)) - jnp.log(b),
                lambda b: jnp.log(jnp.power(self._low, b) - jnp.power(x, b)) - jnp.log(-b),
                self._beta,
            ), self._beta)
        logcdf_val -= self._logZ
        logcdf_val = jnp.where(x >= self._low, logcdf_val, -jnp.inf)
        logcdf_val = jnp.where(x <= self._high, logcdf_val, jnp.log(1.0))
        return logcdf_val

    @partial(jax.jit, static_argnums=(0,))
    def logcdfinv(self, x: ArrayLike) -> ArrayLike:
        logcdfinv_val = lax.cond(
            self._alpha == -1.0,
            lambda _: x * jnp.log(self._high) + (1.0 - x) * jnp.log(self._low),
            lambda b: (1.0 / b) * jnp.log(x * b * self.Z() + jnp.power(self._low, b)),
            self._beta,
        )
        logcdfinv_val = jnp.where(x >= 0.0, logcdfinv_val, -jnp.inf)
        logcdfinv_val = jnp.where(x <= 1.0, logcdfinv_val, jnp.log(1.0))
        return logcdfinv_val

    def logrvs(self, N: int = 1) -> Array:
        U = jax.random.uniform(self.get_key(), shape=(N,), dtype=jnp.float32)
        logrvs_val = self.logcdfinv(U)
        return logrvs_val

    def __repr__(self) -> str:
        string = f"TruncPowerLaw(alpha={self._alpha}, low={self._low}, high={self._high}"
        if self._name is not None:
            string += f", name={self._name}"
        return string + ")"
