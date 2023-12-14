from functools import partial

import jax
from jax import Array, jit

from jax.scipy.stats import beta as jax_beta
from jax.typing import ArrayLike
from tensorflow_probability.substrates import jax as tfp

from .crvs import ContinuousRV


class Beta(ContinuousRV):

    def __init__(self, alpha: float, beta: float, name: str = None) -> None:
        self._alpha = alpha
        self._beta = beta
        self.check_params()
        super().__init__(name)

    def check_params(self) -> None:
        assert self._alpha > 0.0, "alpha must be positive"
        assert self._beta > 0.0, "beta must be positive"

    @partial(jit, static_argnums=(0,))
    def logpdf(self, x: ArrayLike) -> ArrayLike:
        return jax_beta.logpdf(x, self._alpha, self._beta)

    @partial(jit, static_argnums=(0,))
    def pdf(self, x: ArrayLike) -> ArrayLike:
        return jax_beta.pdf(x, self._alpha, self._beta)

    @partial(jit, static_argnums=(0,))
    def logcdf(self, x: ArrayLike) -> ArrayLike:
        return jax_beta.logcdf(x, self._alpha, self._beta)

    @partial(jit, static_argnums=(0,))
    def cdf(self, x: ArrayLike) -> ArrayLike:
        return jax_beta.cdf(x, self._alpha, self._beta)

    @partial(jit, static_argnums=(0,))
    def ppf(self, x: ArrayLike) -> ArrayLike:
        return tfp.math.betaincinv(self._alpha, self._beta, x)

    def rvs(self, N: int = 1, key: Array = None) -> Array:
        if key is None:
            key = self.get_key()
        return jax.random.beta(key, self._alpha, self._beta, shape=(N,))

    def __repr__(self) -> str:
        string = f"beta(alpha={self._alpha}, beta={self._beta}"
        if self._name is not None:
            string += f", name={self._name}"
        return string + ")"
