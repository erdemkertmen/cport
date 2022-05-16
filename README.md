[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![python lint](https://github.com/haddocking/cport/actions/workflows/lint.yml/badge.svg)](https://github.com/haddocking/cport/actions/workflows/lint.yml)
[![unittests](https://github.com/haddocking/cport/actions/workflows/unittests.yml/badge.svg)](https://github.com/haddocking/cport/actions/workflows/unittests.yml)
[![codecov](https://codecov.io/gh/haddocking/cport/branch/main/graph/badge.svg?token=18GQSVO3PF)](https://codecov.io/gh/haddocking/cport)

# CPORT: Consensus Prediction Of interface Residues in Transient complexes

*CPORT is an algorithm for the prediction of protein-protein interface residues.*

***

## DISCLAIMER

This repository contains an **ongoing development** of the next version of CPORT, and as such it is not stable yet. The codebase might change drastically in the future.

For the current stable version, please access the web service at [https://alcazar.science.uu.nl/services/CPORT](https://alcazar.science.uu.nl/services/CPORT/).

Please also refer to the original publication:

- de Vries, S. J. & Bonvin, A. M. J. J. [CPORT: A Consensus Interface Predictor and Its Performance in Prediction-Driven Docking with HADDOCK](https://doi.org/10.1371/journal.pone.0017695). PLoS ONE vol. 6 e17695 (2011).

***

## Predictors

| Server | Status | Implemented |
|---|---|---|
| [WHISCY](https://wenmr.science.uu.nl/whiscy/) | 🟢 | ✔️ |
| [SCRIBER](http://biomine.cs.vcu.edu/servers/SCRIBER/) | 🟢 | ✔️ |
| [ISPRED4](https://ispred4.biocomp.unibo.it/ispred/default/index) | 🟢 | ✔️ |
| [BSpred](https://zhanggroup.org/BSpred/) | 🟠 |  |
| [DELPHI](https://delphi.csd.uwo.ca) | 🟠 |  |
| [MASIF-site](https://github.com/LPDI-EPFL/masif) | 🟢 |  |
| [SPPIDER](https://sppider.cchmc.org) | 🟢 | ✔️ |
| [ProMate](http://bioportal.weizmann.ac.il/promate/) | 🔴 |  |
| [meta-PPISP](https://pipe.rcc.fsu.edu/meta-ppisp.html) | 🟢 |  |
| [PredUs2](http://honig.c2b2.columbia.edu/predus) | 🟢 | ✔️ |
| [Cons-PPISP](https://pipe.rcc.fsu.edu/ppisp.html) | 🟢 | ✔️ |
| [PredictProtein](https://predictprotein.org) | 🟢 | ✔️ |

## Installation

```text
git clone https://github.com/haddocking/cport.git
cd cport
python setup.py develop
cport
```

## Example

```text
cport 1PPE E
```
