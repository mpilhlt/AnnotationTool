TEIVorlage = '''<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>
<?teipublisher template="view-grid.html" view="single"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="NSRMI_$SRCID">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title type="short">$SHORTTITLE</title>
                <title type="main">$TITLE</title>
                <author/>
            
                <editor xml:id="PC" role="#scholarly">
                    <persName ref="gnd:122339479">
                        <surname full="yes">Collin</surname>, <forename full="yes">Peter</forename>
                    </persName>
                </editor>
                <editor xml:id="JW" role="#scholarly">
                    <persName ref="orcid:0000-0001-6364-8902 gnd:1124952586">
                        <surname full="yes">Wolf</surname>, <forename full="yes">Johanna</forename>
                    </persName>
                </editor>
                <editor xml:id="ME" role="#scholarly">
                    <persName ref="orcid:0000-0001-6440-2453">
                        <surname full="yes">Ebbertz</surname>, <forename full="yes">Matthias</forename>
                    </persName>
                </editor>
                <editor xml:id="TV" role="#scholarly">
                    <persName>
                        <surname full="yes">Vespers</surname>, <forename full="yes">Tim</forename>
                    </persName>
                </editor>
                <editor xml:id="AW" role="#technical">
                    <persName ref="orcid:0000-0003-1835-1653">
                        <surname>Wagner</surname>, <forename>Andreas</forename>
                    </persName>
                </editor>
                <editor xml:id="PS" role="#technical">
                    <persName>
                        <surname>Solonets</surname>, <forename>Polina</forename>
                    </persName>
                </editor>
                <editor xml:id="BS" role="#technical">
                    <persName>
                        <surname>Spendrin</surname>, <forename>Benjamin</forename>
                    </persName>
                </editor>
                <editor xml:id="BG" role="#technical">
                    <persName>
                        <surname>Gödde</surname>, <forename>Ben</forename>
                    </persName>
                </editor>
                <editor xml:id="LM" role="#technical">
                    <persName>
                        <surname>Michel</surname>, <forename>Lisa</forename>
                    </persName>
                </editor>
                <editor xml:id="AWt" role="#technical">
                    <persName>
                        <surname>Walther</surname>, <forename>Annika</forename>
                    </persName>
                </editor>
            </titleStmt>

            <editionStmt>
                <edition n="1.0.0">
                    Complete digital edition, <date type="digitizedEd" when="$WHEN">$WHEN</date>.
                </edition>
            </editionStmt>

            <publicationStmt>
                <publisher xml:id="pubstmt-publisher">
                    <orgName>Max Planck Institute for Legal History and Legal Theory</orgName>
                    <ref type="url" target="http://www.lhlt.mpg.de/">http://www.lhlt.mpg.de/</ref>
                </publisher>
                <distributor xml:id="pubstmt-distributor">
                    <orgName>Max Planck Institute for Legal History and Legal Theory</orgName>
                    <ref type="url" target="http://www.lhlt.mpg.de/">http://www.lhlt.mpg.de/</ref>
                </distributor>
                <pubPlace role="digitizedEd" xml:id="pubstmt-pubplace">
                    Frankfurt am Main, Germany
                </pubPlace>
                <availability xml:id="pubstmt-availability">
                    <licence target="https://creativecommons.org/licenses/by/4.0" n="cc-by">
                        <p xml:id="p_ffjaztskfd">This work or content, respectively, was created for the Max Planck Institute for Legal
                            History and Legal Theory, Frankfurt/M., and is licensed under the terms of a
                            <ref target="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International (CC BY 4.0)</ref>.</p>
                    </licence>
                </availability>
                <date type="digitizedEd" when="$WHEN">$WHEN</date>
            </publicationStmt>

            <seriesStmt xml:id="seriesStmt">
                <title level="s">Nichtstaatliches Recht der Wirtschaft</title>
                <editor ref="#PC"/>
                <editor ref="#JW"/>
            </seriesStmt>

            <sourceDesc>
                <bibl>
                    
                    <date when="$SRCYEAR">$SRCYEAR</date>
                    <note>According to: <bibl>$SRCBIBL.</bibl></note>
                </bibl>
                
                
            </sourceDesc>
        </fileDesc>

        <encodingDesc>
            <listPrefixDef>
                <prefixDef ident="nsrmi" matchPattern="([A-z0-9.:#_\-]+)" replacementPattern="http://c100-172.cloud.gwdg.de:8080/exist/apps/metallindustrie/api/document/taxonomy.xml#$1">
                   <p xml:id="p_f2q34f3cew" xml:lang="en">Within the scope of this edition, pointers using an "nsrmi" prefix are private URIs and refer to 
                       taxonomies and entity description defined in the "taxonomy.xml" file in the "metall-data" directory of this app.
                       These definitions can accessed via web
                       under the address <ref type="url" target="http://c100-172.cloud.gwdg.de:8080/exist/apps/metallindustrie/api/document/taxonomy.xml">http://c100-172.cloud.gwdg.de:8080/exist/apps/metallindustrie/api/document/taxonomy.xml</ref>, 
                       which is to be complemented by the identifier (what comes after the "nsrmi:" prefix), prepended by a "#" passage identifier, e.g.
                       <ref type="url" target="http://c100-172.cloud.gwdg.de:8080/exist/apps/metallindustrie/api/document/taxonomy.xml#kategorie">http://c100-172.cloud.gwdg.de:8080/exist/apps/metallindustrie/api/document/taxonomy.xml#kategorie</ref>.</p>
                </prefixDef>
            </listPrefixDef>
        </encodingDesc>

        <profileDesc>
            <textClass>
               <catRef scheme="nsrmi:kategorie" target="nsrmi:NSRMI_Arbeitsordnungen"/>
               <catRef scheme="nsrmi:key" target="nsrmi:NSRMI_MI"/>
            </textClass>
        </profileDesc>

        <revisionDesc>
            <listChange>
                <change when="$WHEN" who="#auto #AW">Compile TEI from PageXML sources</change>
            </listChange>
        </revisionDesc>
    </teiHeader>
      
    <text>
        <body>
            
            <p>
                $SRCTEXT
            </p>
            
        </body>
    </text>
</TEI>'''