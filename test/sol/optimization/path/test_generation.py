# coding=utf-8
import pytest
from sol.optimization.path.generate import generatePathsPerIE
from sol.optimization.path.predicates import nullPredicate, UseMboxModifier
from sol.optimization.topology.generators import generateChainTopology, \
    generateCompleteTopology
from sol.optimization.topology.traffic import PathWithMbox
from sol.util.exceptions import NoPathsException


def test_pathgen_simple():
    """
    Check that one path is found on chain topology
    """
    chaintopo = generateChainTopology(5)
    for sink in xrange(1, 5):
        pptc = generatePathsPerIE(0, sink, chaintopo, nullPredicate, cutoff=100)
        print pptc
        assert len(pptc) == 1

    with pytest.raises(NoPathsException):
        generatePathsPerIE(0, 4, chaintopo, lambda p, t: False, 100)

    chaintopo.getGraph().remove_edge(1, 2)
    with pytest.raises(NoPathsException):
        generatePathsPerIE(0, 4, chaintopo, nullPredicate, 100)
    assert len(generatePathsPerIE(0, 4, chaintopo, nullPredicate, cutoff=100,
                                  raiseOnEmpty=False)) == 0

def test_pathgen_cutoffs():
    t = generateCompleteTopology(8)
    pptc = generatePathsPerIE(1, 3, t, nullPredicate, 100)
    assert len(pptc) > 20
    pptc = generatePathsPerIE(1, 3, t, nullPredicate, 1)
    assert len(pptc) == 1
    pptc = generatePathsPerIE(1, 3, t, nullPredicate, 2)
    assert len(pptc) == 7
    pptc = generatePathsPerIE(1, 3, t, nullPredicate, 100, maxPaths=4)
    assert len(pptc) == 4


def test_pathgen_mbox():
    t = generateCompleteTopology(8)
    def mbox(path, topology):
        G = topology.getGraph()
        return [PathWithMbox(path, [n]) for n in path]

    pptc = generatePathsPerIE(1, 3, t, nullPredicate, 2,
                              modifyFunc=mbox)
    assert len(pptc) == 20

    t.getGraph().node[1]['hasmbox'] = True
    t.getGraph().node[3]['hasmbox'] = True
    pptc = generatePathsPerIE(1, 3, t, nullPredicate, 2,
                              modifyFunc=UseMboxModifier)
    assert len(pptc) == 14