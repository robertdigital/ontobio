from ontobio.ontol_factory import OntologyFactory

PART_OF = 'BFO:0000050'
NUCLEUS='GO:0005634'
INTRACELLULAR='GO:0005622'
INTRACELLULAR_PART='GO:0044424'
IMBO = 'GO:0043231'
CELL = 'GO:0005623'
CELLULAR_COMPONENT = 'GO:0005575'
WIKIPEDIA_CELL = 'Wikipedia:Cell_(biology)'
NIF_CELL = 'NIF_Subcellular:sao1813327414'
CELL_PART = 'GO:0044464'

def test_obo_read():
    ont = OntologyFactory().create("tests/resources/goslim_pombe.obo")

    assert len(ont.graph) == 54


def test_graph():
    """
    Load ontology from JSON
    """
    factory = OntologyFactory()
    print("Creating ont")
    ont = factory.create('tests/resources/nucleus.obo')
    # assert ont.id == 'http://purl.obolibrary.org/obo/go-test.owl'

    icp = ont.node(INTRACELLULAR_PART)
    print("ICP: {}".format(icp))
    assert ont.label(INTRACELLULAR_PART) == 'intracellular part'

    assert ont.node_type(INTRACELLULAR_PART) == 'CLASS'

    graph = ont.get_graph()
    print("GRAPH: {}".format(graph.nodes))

    ancs = ont.ancestors(NUCLEUS)
    print("ANCS nucleus (all): {}".format(ancs))
    assert CELL in ancs
    assert CELLULAR_COMPONENT in ancs
    assert INTRACELLULAR in ancs
    assert NUCLEUS not in ancs

    ancs = ont.ancestors(INTRACELLULAR_PART)
    print("ANCS intracellular part(all): {}".format(ancs))
    assert CELL in ancs
    assert CELLULAR_COMPONENT in ancs
    assert NUCLEUS not in ancs

    ancs = ont.ancestors(INTRACELLULAR_PART, relations=['subClassOf'])
    print("ANCS intracellular part(subclass): {}".format(ancs))
    assert CELLULAR_COMPONENT in ancs
    assert CELL not in ancs
    assert NUCLEUS not in ancs

    # note: queries over *only* part_of are a non-use case, as we
    # typically always include subClassOf, due to how these chain
    # together according to OWL semantics
    ancs = ont.ancestors(INTRACELLULAR_PART, relations=[PART_OF])
    print("ANCS intracellular part(part_of): {}".format(ancs))
    assert INTRACELLULAR in ancs
    assert CELL not in ancs
    assert NUCLEUS not in ancs

    ancs = ont.parents(INTRACELLULAR_PART)
    print("PARENTS intracellular (all): {}".format(ancs))
    assert INTRACELLULAR in ancs
    assert CELL_PART in ancs
    assert CELLULAR_COMPONENT not in ancs
    assert NUCLEUS not in ancs

    ancs = ont.parents(INTRACELLULAR_PART, relations=[PART_OF])
    print("PARENTS intracellular (part_of): {}".format(ancs))
    assert INTRACELLULAR in ancs
    assert CELL_PART not in ancs
    assert CELLULAR_COMPONENT not in ancs
    assert NUCLEUS not in ancs

    decs = ont.descendants(INTRACELLULAR_PART)
    print("DECS: {}".format(decs))
    assert NUCLEUS in decs
    assert CELL not in decs

    decs = ont.descendants(INTRACELLULAR, relations=[PART_OF])
    print("DECS: {}".format(decs))
    assert INTRACELLULAR_PART in decs
    assert NUCLEUS not in decs
    assert CELL not in decs

    decs = ont.children(INTRACELLULAR)
    print("CHILDREN (all): {}".format(decs))
    assert [INTRACELLULAR_PART] == decs

    decs = ont.children(CELL_PART)
    print("CHILDREN (all): {}".format(decs))
    assert INTRACELLULAR_PART in decs
    assert INTRACELLULAR in decs

    decs = ont.children(INTRACELLULAR, relations=[PART_OF])
    print("CHILDREN (po): {}".format(decs))
    assert INTRACELLULAR_PART in decs
    assert NUCLEUS not in decs
    assert CELL not in decs

    xrefs = ont.xrefs(CELL)
    print("XREFS (from GO): {}".format(xrefs))
    assert WIKIPEDIA_CELL in xrefs
    assert NIF_CELL in xrefs
    assert len(xrefs) == 2

    # xrefs are bidirectional
    xrefs = ont.xrefs(WIKIPEDIA_CELL, bidirectional=True)
    print("XREFS (from WP, bidi): {}".format(xrefs))
    assert CELL in xrefs
    assert len(xrefs) == 1

    # xrefs queries unidirectional by default
    xrefs = ont.xrefs(WIKIPEDIA_CELL)
    print("XREFS (from WP): {}".format(xrefs))
    assert len(xrefs) == 0

    tdef = ont.text_definition(NUCLEUS)
    print("TDEF: {}".format(tdef))
    assert tdef.xrefs == ["GOC:go_curators"]
    assert tdef.val.startswith("A membrane-bounded organelle of eukaryotic cells in which")

    [ldef] = ont.logical_definitions(INTRACELLULAR_PART)
    print("LDEF: {}".format(ldef))
    assert ldef.genus_ids == [CELLULAR_COMPONENT]
    assert ldef.restrictions == [(PART_OF, INTRACELLULAR)]

    syns = ont.synonyms(CELL_PART, include_label=True)
    print("SYNS: {}".format(syns))
    [s1] = [x for x in syns if x.val == 'protoplast']
    assert s1.pred == 'hasRelatedSynonym'
    assert s1.xrefs == ['GOC:mah']

    GOSLIM = 'goslim_generic'
    subsets = ont.subsets(NUCLEUS)
    print("SUBSETS: {}".format(subsets))
    assert GOSLIM in subsets
    assert len(subsets) > 0

    in_slim = ont.extract_subset(GOSLIM)
    print("IN SLIM: {}".format(in_slim))
    assert len(in_slim) > 0
    assert NUCLEUS in in_slim

    # logging.basicConfig(level=logging.DEBUG)

    assert [] == ont.search('protoplast', synonyms=False)
    assert {CELL_PART, INTRACELLULAR} == set(ont.search('protoplast', synonyms=True))

    assert ont.has_node(CELL_PART)
    assert not ont.has_node('FOO:123')

    # relations
    assert ont.label(PART_OF) == 'part of'
    assert ont.node_type(PART_OF) == 'PROPERTY'

    # ensure subontology retains properties
    decs = ont.descendants(CELL, reflexive=True)
    subont = ont.subontology(nodes=decs)

    syns = subont.synonyms(CELL_PART, include_label=True)
    print("SYNS: {}".format(syns))
    [s1] = [x for x in syns if x.val == 'protoplast']
    assert s1.pred == 'hasRelatedSynonym'
    assert s1.xrefs == ['GOC:mah']

    assert subont.parents(NUCLEUS) == [IMBO]

    from ontobio import GraphRenderer
    w = GraphRenderer.create('obo')
    w.write(subont, query_ids=[CELL, CELL_PART, NUCLEUS])