#  Copyright 2023 The Jaxampler Authors
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

from functools import partial
from typing import Any, Optional

import jax
from jax import Array, jit, numpy as jnp
from jax.scipy.stats import poisson as jax_poisson

from ..typing import Numeric
from ..utils import jx_cast
from .drvs import DiscreteRV


class Poisson(DiscreteRV):
    def __init__(self, mu: Numeric | Any, loc: Numeric | Any = 0.0, name: Optional[str] = None) -> None:
        shape, self._mu, self._loc = jx_cast(mu, loc)
        self.check_params()
        super().__init__(name=name, shape=shape)

    def check_params(self) -> None:
        assert jnp.all(self._mu > 0.0), "Lambda must be positive"

    @partial(jit, static_argnums=(0,))
    def logpmf_x(self, x: Numeric) -> Numeric:
        return jax_poisson.logpmf(
            k=x,
            mu=self._mu,
            loc=self._loc,
        )

    @partial(jit, static_argnums=(0,))
    def pmf_x(self, x: Numeric) -> Numeric:
        return jax_poisson.pmf(
            k=x,
            mu=self._mu,
            loc=self._loc,
        )

    @partial(jit, static_argnums=(0,))
    def logcdf_x(self, x: Numeric) -> Numeric:
        return jnp.log(self.cdf_x(x))

    @partial(jit, static_argnums=(0,))
    def cdf_x(self, x: Numeric) -> Numeric:
        return jax_poisson.cdf(
            k=x,
            mu=self._mu,
            loc=self._loc,
        )

    def rvs(self, shape: tuple[int, ...], key: Optional[Array] = None) -> Array:
        if key is None:
            key = self.get_key()
        new_shape = shape + self._shape
        return jax.random.poisson(key, self._mu, shape=new_shape)

    def __repr__(self) -> str:
        string = f"Poisson(lmbda={self._mu}"
        if self._name is not None:
            string += f", name={self._name}"
        string += ")"
        return string
