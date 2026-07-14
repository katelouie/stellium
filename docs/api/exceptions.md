# Exceptions & Warnings

Stellium prefers to *warn and continue* rather than fail, because most of what it
has to complain about is a data problem rather than a programming error: a birth
time nobody recorded, a place a geocoder has never heard of, an ephemeris file that
was never downloaded, a glyph the font does not contain.

Every one of these is a subclass of {py:class}`~stellium.exceptions.StelliumWarning`,
so you can escalate the whole family at once — which is what you want in a pipeline,
where a silent warning is how a wrong chart reaches a user:

```python
import warnings
from stellium import StelliumWarning

warnings.simplefilter("error", StelliumWarning)   # every data-quality warning is now fatal
```

Or catch them and decide for yourself. Zaha Hadid's record carries a clock time, and
the audit marked that time unreliable — so asking for it anyway says so out loud:

```python
import warnings
from stellium import ChartBuilder, DataQualityWarning

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always", DataQualityWarning)
    chart = ChartBuilder.from_notable("Zaha Hadid", use_recorded_time=True).calculate()

print(caught[0].category.__name__)
print(chart.metadata["time_provenance"]["source"])
```

<!--pytest-codeblocks:expected-output-->

```
DataQualityWarning
recorded_time_override
```

The chart still gets built — the warning is not a refusal. But the provenance rides
along with it in `chart.metadata["time_provenance"]`, so a report drawn from that
chart can say where its houses came from instead of quietly presenting them as fact.

```{eval-rst}
.. automodule:: stellium.exceptions
   :members:
   :undoc-members:
   :show-inheritance:
```

## Logging

Warnings say "this chart may be wrong." Logging says "here is what was done." The
library emits no output of its own unless you ask it to.

```{eval-rst}
.. automodule:: stellium._logging
   :members:
   :undoc-members:
   :show-inheritance:
```
