import os

__all__ = [x[:-3]
           for x in os.listdir(os.path.dirname(__file__))
           if x.endswith('.py') and x!='__init__.py']
modules=[__import__('plugins.%s' % m, globals(), locals(), ['convert'], -1)
         for m in __all__]
