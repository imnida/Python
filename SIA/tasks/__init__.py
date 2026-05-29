"""Task definitions for the three SIA benchmark domains."""
from .lawbench import LawBenchTask
from .trimul import TriMulTask
from .scrnaseq import SCRNASeqTask

__all__ = ["LawBenchTask", "TriMulTask", "SCRNASeqTask"]
