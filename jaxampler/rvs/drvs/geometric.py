from functools import partial

import jax
from jax import Array, jit
from jax import numpy as jnp

from jax.scipy.stats import geom as jax_geom
from jax.typing import ArrayLike

from .drvs import DiscreteRV


class Geometric(DiscreteRV):

    def __init__(self, p: float, name: str = None) -> None:
        self._p = p
        self.check_params()
        self._q = 1.0 - self._p
        super().__init__(name)

    def check_params(self) -> None:
        assert self._p >= 0.0, "All p must be greater than or equals to 0"

    @partial(jit, static_argnums=(0,))
    def logpmf(self, k: ArrayLike) -> ArrayLike:
        return jax_geom.logpmf(k, self._p)

    @partial(jit, static_argnums=(0,))
    def pmf(self, k: ArrayLike) -> ArrayLike:
        return jax_geom.pmf(k, self._p)

    @partial(jit, static_argnums=(0,))
    def cdf(self, k: ArrayLike) -> ArrayLike:
        conditions = [k < 0, k >= 0]
        choices = [jnp.zeros_like(k), 1.0 - jnp.power(self._q, jnp.floor(k))]
        return jnp.select(conditions, choices)

    @partial(jit, static_argnums=(0,))
    def logcdf(self, k: ArrayLike) -> ArrayLike:
        return jnp.log(self.cdf(k))

    def rvs(self, N: int = 1, key: Array = None) -> Array:
        if key is None:
            key = self.get_key()
        return jax.random.geometric(key, self._p, shape=(N,))

    def __repr__(self) -> str:
        string = f"Geometric(p={self._p}"
        if self._name is not None:
            string += f", (name: {self._name}"
        return string + ")"
