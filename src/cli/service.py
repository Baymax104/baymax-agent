# -*- coding: UTF-8 -*-
from injection import Container


container = Container()
container.wire(modules=[__name__])
