from functools import partial

import jax
from jax import Array, jit
from jax.random import KeyArray
from jax.scipy.stats import chi2 as jax_chi2
from jax.typing import ArrayLike

from .crvs import ContinuousRV


class Chi2(ContinuousRV):

    def __init__(self, nu: float, name: str = None) -> None:
        self._nu = nu
        self.check_params()
        super().__init__(name)

    def check_params(self) -> None:
        assert self._nu % 1 == 0, "nu must be an integer"

    @partial(jit, static_argnums=(0,))
    def logpdf(self, x: ArrayLike) -> ArrayLike:
        return jax_chi2.logpdf(x, self._nu)

    @partial(jit, static_argnums=(0,))
    def pdf(self, x: ArrayLike) -> ArrayLike:
        return jax_chi2.pdf(x, self._nu)

    @partial(jit, static_argnums=(0,))
    def logcdf(self, x: ArrayLike) -> ArrayLike:
        return jax_chi2.logcdf(x, self._nu)

    @partial(jit, static_argnums=(0,))
    def cdf(self, x: ArrayLike) -> ArrayLike:
        return jax_chi2.cdf(x, self._nu)

    @partial(jit, static_argnums=(0,))
    def logppf(self, x: ArrayLike) -> ArrayLike:
        raise NotImplementedError("Not able to find sufficient information to implement")

    def rvs(self, N: int = 1, key: KeyArray = None) -> Array:
        if key is None:
            key = self.get_key()
        return jax.random.chisquare(key, self._nu, shape=(N,))

    def __repr__(self) -> str:
        string = f"Chi2(nu={self._nu}"
        if self._name is not None:
            string += f", name={self._name}"
        return string + ")"
