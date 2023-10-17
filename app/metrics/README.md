# List of metrics

Note that all the following metrics must be implemented to work on `.omex` archives.

## Resources

Existing metrics implementations were found in the [Rare Disease Fair Metrics Github](https://github.com/LUMC-BioSemantics/RD-FAIRmetric-F4)
and in the [Fair Enough Metrics Github](https://github.com/MaastrichtU-IDS/fair-enough-metrics).

All FairCombine indicators are defined in the project issues on [github](https://github.com/FAIR-CA-indicators/CA-RDA-Indicators/issues?page=2&q=is%3Aissue+is%3Aopen).
See the `help wanted` tag.

The Combine specifications are defined on [github](https://github.com/combine-org/combine-specifications)

## Findable

### F1: Data and metadata identifiers:

1. CA-RDA-F1-01Archive - Archive is identified by a persistent identifier
2. CA-RDA-F1-01Model - Model is identified by a persistent identifier
3. CA-RDA-F1-01MA - Metadata of archive is identified by a persistent identifier
4. CA-RDA-F1-01MM - Metadata of model is identified by a persistent identifier
5. CA-RDA-F1-02Archive - Archive is identified by a globally unique identifier
6. CA-RDA-F1-02Model - Model is identified by a globally unique identifier
7. CA-RDA-F1-02MA - Metadata of archive is identified by a globally unique identifier
8. CA-RDA-F1-02MM - Metadata of model is identified by a globally unique identifier

Both `1.` and `3.` can be associated with [f1_data_identifier_persistent](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/f1_data_identifier_persistent.py).
`3.` and `4.` can be associated with [f1_metadata_identifier_persistent](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/f1_metadata_identifier_persistent.py).
`5.` and `6.` are not related to any test in `fair-enough-metrics`, but something may be used from the metadata globally unique identifier [f1_metadata_identifier_unique](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/f1_metadata_identifier_unique.py)
which is associated with `7.` and `8.`.

### F2: Rich metadata provided

1. CA-RDA-F2-01MA - Rich metadata of archive is provided to allow discovery
2. CA-RDA-F2-01MM - Rich metadata of model is provided to allow discovery

Both of these need some definition about what constitutes **Rich** metadata.
In fair-enough, there are two tests associated with F2, [f2_grounded_metadata](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/f2_grounded_metadata.py)
and [f2_structured_metadata](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/f2_structured_metadata.py),
which respectively test whether the metadata is 'grounded' (i.e. `metadata terms are in a resolvable namespace, where resolution leads to a definition of the meaning of the term.`)
and structured. This second test passes if the metadata is in rdf, json, json-ld or yaml format.

### F3: Metadata contains data identifier

1. CA-RDA-F3-01MA - Metadata of archive includes the identifier for the archive
2. CA-RDA-F3-01MM - Metadata of model includes the identifier for the model

This is done by [f3_data_identifier_in_metadata](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/f3_data_identifier_in_metadata.py),
note that the test checks for a set number of properties, so we could actually apply this on the 
`.omex` format specifically.

### F4: Metadata can be archived and indexed
1. CA-RDA-F4-01MA - Metadata of archive is offered in such a way that it can be harvested and indexed
2. CA-RDA-F4-01MM - Metadata of model is offered in such a way that it can be harvested and indexed

fair_enough does it with [f4_searchable](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/f4_searchable.py).

The test searches for a doi, then check in DataCite that the doi is findable (should it check zenodo? also).
If it does, it then runs a query in Google and in Bing and tries to find our expected uri in the results.

DuckDuckGo was also used at first, but it seems they blocked the fair_enough server.

# Accessible

## A1: Data and Metadata accessibility

1. CA-RDA-A1-01MA - Metadata of archive contains information to enable the user to get access to the archive
2. CA-RDA-A1-01MM - Metadata of model contains information to enable the user to get access to the model
3. CA-RDA-A1-02Archive - Archive can be accessed manually (i.e. with human intervention)
4. CA-RDA-A1-02Model - Model can be accessed manually (i.e. with human intervention)
5. CA-RDA-A1-02MA - Metadata of archive can be accessed manually (i.e. with human intervention)
6. CA-RDA-A1-02MM - Metadata of model can be accessed manually (i.e. with human intervention)
7. CA-RDA-A1-03Archive - Archive identifier resolves to a digital object
8. CA-RDA-A1-03Model - Model identifier resolves to a digital object
9. CA-RDA-A1-03MA - Metadata of archive identifier resolves to a metadata of archive record
10. CA-RDA-A1-03MM - Metadata of model identifier resolves to a metadata of model record
11. CA-RDA-A1-04Archive - Archive is accessible through standardised protocol
12. CA-RDA-A1-04Model - Model is accessible through standardised protocol
13. CA-RDA-A1-04MA - Metadata of archive is accessed through standardised protocol
14. CA-RDA-A1-04MM - Metadata of model is accessed through standardised protocol
15. CA-RDA-A1-05Archive - Archive can be accessed automatically (i.e. by a computer program)
16. CA-RDA-A1-05Model - Model can be accessed automatically (i.e. by a computer program)

`1.` and `2.` seems to relate to principle `A.1.2` (The protocol allows for an authentication and authorisation procedure where necessary)
These two may be hard to test programmatically, check for omex keywords and see if any relate to data location or
access protocol?
Note that [a1_metadata_authorization](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/a1_metadata_authorization.py)
seems to be doing that.

`3.`, `4.`, `5.` and `6.` should be manual I think. The user just has to say if they can access the data (once identified if not public).

`7.` and `8.` test whether the data identifier points toward the data record. I.e. can you use the data GUID to access the record.
If ID is a url or doi, answer is yes. May be useful to check that the record is the correct one (how?).
May be related to [a1_data_protocol](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/a1_data_protocol.py)
or [a1_access_protocol](/example/metrics/a1_access_protocol.py).

`9.` and `10.` are the same idea than `7.` and `8.`, but for metadata.

`11.` to `14.` are actually implemented in [a1_data_protocol](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/a1_data_protocol.py),
[a1_metadata_protocol](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/a1_metadata_protocol.py), 
[local a1_metadata_protocol](/example/metrics/a1_metadata_protocol.py) and [local a1_access_protocol](/example/metrics/a1_access_protocol.py).

For `15.` and `16.`, check that the identifiers given resolve to an object? If it does, the answer is clearly yes.
May be manually set also, as it depends on whether the data requires authentication or not.
Assuming there is no authentication needed, is there any API to access archive/model?

## A1.1. & A1.2.: (Meta)data access protocol

1. CA-RDA-A1.1-01Archive - Archive is accessible through a free access protocol
2. CA-RDA-A1.1-01Model - Model is accessible through a free access protocol
3. CA-RDA-A1.1-01MA - Metadata of archive is accessible through a free access protocol
4. CA-RDA-A1.1-01MM - Metadata of model is accessible through a free access protocol
5. CA-RDA-A1.2-01Archive - Archive is accessible through an access protocol that supports authentication and authorisation
6. CA-RDA-A1.2-01Model - Model is accessible through an access protocol that supports authentication and authorisation

`1.` to `4.` extends the indicators defined `11.` to `14.` defined in the previous section.
In brief, a protocol can be standardised without being free or open.
These indicators asserts that the protocol to access data and metadata are free of charge.

`5.` and `6.` asserts that the protocol used to access archive and model supports authentication
and authorization. [a1_metadata_authorization](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/a1_metadata_authorization.py)
may be adapted to the implementation of these two assessments.

## A2: (Meta)data persistence

1. CA-RDA-A2-01MA - Metadata of archive is guaranteed to remain available after archive is no longer available
2. CA-RDA-A2-01MM - Metadata of model is guaranteed to remain available after model is no longer available

Both of these are implemented in [a2_metadata_persistent](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/a2_metadata_persistent.py)


# Interoperability

## I1: (Meta)data representation format

1. CA-RDA-I1-01Archive - Archive content is expressed in standardised formats
2. CA-RDA-I1-01Model - Model content is expressed in standardised formats
3. CA-RDA-I1-01MA - Metadata of archive is expressed in standardised formats
4. CA-RDA-I1-01MM - Metadata of model is expressed in standardised formats
5. CA-RDA-I1-02Archive - Archive uses machine-understandable knowledge representation
6. CA-RDA-I1-02Model - Model uses machine-understandable knowledge representation
7. CA-RDA-I1-02MA - Metadata of archive uses machine-understandable knowledge representation
8. CA-RDA-I1-02MM - Metadata of model uses machine-understandable knowledge representation

All of these can probably be automated using content from [i1_data_knowledge_representation_semantic](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/i1_data_knowledge_representation_semantic.py), 
[i1_data_knowledge_representation_structured](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/i1_data_knowledge_representation_structured.py),
[i1_metadata_knowledge_representation_semantic](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/i1_metadata_knowledge_representation_semantic.py),
and [i1_metadata_knowledge_representation_structured](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/i1_metadata_knowledge_representation_structured.py)

## I2: (Meta)data use of FAIR-compliant vocabulary

1. CA-RDA-I2-01Archive - The files contained in the Archive use FAIR-compliant vocabularies 
2. CA-RDA-I2-01Model - Model uses FAIR-compliant vocabularies 
3. CA-RDA-I2-01MA - Metadata of archive uses FAIR-compliant vocabularies 
4. CA-RDA-I2-01MM - Metadata of model uses FAIR-compliant vocabularies

Some open namespaces are defined in [i2_fair_vocabularies_known](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/i2_fair_vocabularies_known.py).
See also the list of [Linked Open Vocabularies](https://lov.linkeddata.es/dataset/lov).


## I3: (Meta)data references to other (meta)data

1. CA-RDA-I3-01Archive - Archive includes references to other data 
2. CA-RDA-I3-01Model - Model includes references to other data 
3. CA-RDA-I3-01MA - Metadata of archive includes references to other metadata of archive 
4. CA-RDA-I3-01MM - Metadata of model includes references to other metadata of model 
5. CA-RDA-I3-02Archive - Archive includes qualified references to other data 
6. CA-RDA-I3-02Model - Model includes qualified references to other data 
7. CA-RDA-I3-02MA - Metadata of archive includes references to other data (models or archives)
8. CA-RDA-I3-02MM - Metadata of model includes references to other data (archives or models)
9. CA-RDA-I3-03MA - Metadata of archive includes qualified references to other metadata 
10. CA-RDA-I3-03MM - Metadata of model includes qualified references to other metadata 
11. CA-RDA-I3-04MA - Metadata of archive include qualified references to other data 
12. CA-RDA-I3-04MM - Metadata of model include qualified references to other data

References to other data and or archive can be tested in the same way than in [i3_metadata_contains_outward_links](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/i3_metadata_contains_outward_links.py).
A reference is qualified if the relationship role of the related resource is specified, 
for example that a particular link is a specification of a unit of measurement, 
or the identification of the sensor with which the measurement was done.

# Reusability

## R1: (Meta)data richness in accurate attributes
1. CA-RDA-R1-01MA - Plurality of accurate and relevant attributes of archive are provided to allow reuse
2. CA-RDA-R1-01MM - Plurality of accurate and relevant attributes of model are provided to allow reuse

Description of R1 is available on the [FAIR principles website](https://www.go-fair.org/fair-principles/r1-metadata-richly-described-plurality-accurate-relevant-attributes/).
In order to automate this, standard labels should be found. Not a priority to automate, as `plurality of accurate and relevant` is hard to define.

## R1.1.: Data usage license
1. CA-RDA-R1.1-01MA - Metadata of archive includes information about the licence under which the archive can be reused 
2. CA-RDA-R1.1-01MM - Metadata of model includes information about the licence under which the model can be reused 
3. CA-RDA-R1.1-02MA - Metadata of archive refers to a standard reuse licence 
4. CA-RDA-R1.1-02MM - Metadata of model refers to a standard reuse licence 
5. CA-RDA-R1.1-03MA - Metadata of archive refers to a machine-understandable reuse licence 
6. CA-RDA-R1.1-03MM - Metadata of model refers to a machine-understandable reuse licence

`1.` and `2.` are already available in [r1_includes_license](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/r1_includes_license.py).
`3.` and `4.` are already available in [r1_includes_standard_license](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/r1_includes_standard_license.py).
`5.` and `6.` can be automated if we find/define standard license format that are machine-readable.

## R1.2.: Data provenance
1. CA-RDA-R1.2-01MA - Metadata of archive includes provenance information according to community-specific standards 
2. CA-RDA-R1.2-01MM - Metadata of model includes provenance information according to community-specific standards 
3. CA-RDA-R1.2-02MA - Metadata of archive includes provenance information according to a cross-community language 
4. CA-RDA-R1.2-02MM - Metadata of model includes provenance information according to a cross-community language

`1.` and `2.` are automatically true depending on the data provenance. `3.` and `4.` need more definition.

## R1.3.: Community standards
1. CA-RDA-R1.3-01Archive - Archive complies with a community standard 
2. CA-RDA-R1.3-01Model - Model complies with a community standard 
3. CA-RDA-R1.3-01MA - Metadata of archive complies with a community standard 
4. CA-RDA-R1.3-01MM - Metadata of model complies with a community standard 
5. CA-RDA-R1.3-02Archive - Archive is expressed in compliance with a machine-understandable community standard 
6. CA-RDA-R1.3-02Model - Model is expressed in compliance with a machine-understandable community standard 
7. CA-RDA-R1.3-02MA - Metadata of archive is expressed in compliance with a machine-understandable community standard 
8. CA-RDA-R1.3-02MM - Metadata of model is expressed in compliance with a machine-understandable community standard 
9. CA-RDA-R1.3-03MA - Metadata of archive is expressed in compliance with a machine-understandable cross-community standard 
10. CA-RDA-R1.3-03MM - Metadata of model is expressed in compliance with a machine-understandable cross-community standard

All these can be adapted from [r1_community_standard](https://github.com/MaastrichtU-IDS/fair-enough-metrics/blob/main/metrics/r1_community_standard.py).
Either we trust the standard present in the model and archive metadata, or we check using the one in the [Combine specifications github](https://github.com/combine-org/combine-specifications).
Note that standards are defined for the omex archive and the different files (sbml, cellml, ...).
See the [.omex format specification](https://github.com/combine-org/combine-specifications/blob/main/specifications/omex.md) for more information.

