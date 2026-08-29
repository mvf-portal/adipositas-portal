#!/usr/bin/env python3
"""Alles Themenspezifische der taeglichen Studienauswahl — und sonst nichts.

Diese Datei ist die EINZIGE unter scripts/, die sich von Portal zu Portal
inhaltlich unterscheidet. `update_studies.py` bleibt in allen Portalen
wortgleich und importiert von hier. Wer die Auswahl aendern will, aendert
Text in dieser Datei — keinen Code.

Erzeugt von neues-portal.py aus dem Themenprofil `themen/adipositas.json`.
Weiterentwickelt wird danach hier, nicht im Profil.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------- Kennungen
# NCBI bittet bei automatisierten Zugriffen um eine Tool-Kennung.
NCBI_TOOL = "adipositas-portal"

# ----------------------------------------------------------- Die Suchabfrage
# Zwei Bloecke, die BEIDE zutreffen muessen. Ohne den zweiten spuelt die Abfrage
# Arbeiten herein, die das Thema nur streifen; ohne den ersten kommt beliebige
# Versorgungsliteratur.
#
# Zur Feldwahl: [MeSH Terms] fasst breit, [Majr] verlangt das Haupt-Schlagwort,
# [Title/Abstract] fasst am breitesten, [Title] am engsten. Faustregel aus den
# Schwesterportalen: Steht ein Begriff in fremden Abstracts als blosses Werkzeug
# oder Beiwerk, ist [Title/Abstract] untauglich — dann [Majr]/[Title]. Im
# KI-Portal sank die Trefferzahl dadurch von 605.000 auf 321.000, und erst die
# kleinere Menge handelte tatsaechlich vom Thema.
#
# Vor dem Livegang die Trefferzahl in PubMed nachsehen und hier notieren, damit
# spaetere Aenderungen messbar bleiben.
_THEMA = (
    '((("Obesity"[Majr] OR "Obesity, Morbid"[Majr] OR "Pediatric Obesity"[Majr] '
    'OR "Overweight"[Majr] OR "Weight Loss"[Majr] OR "Weight Gain"[Majr] '
    'OR "Bariatric Surgery"[Majr] OR "Bariatrics"[Majr] '
    'OR "Weight Reduction Programs"[Majr] OR "Anti-Obesity Agents"[Majr] '
    'OR "Glucagon-Like Peptide-1 Receptor Agonists"[Majr] '
    'OR "Body Mass Index"[Majr] OR "Metabolic Syndrome"[Majr] '
    'OR "Adiposity"[Majr]) '
    'OR (obesity[Title] OR obese[Title] OR overweight[Title] OR adiposity[Title] '
    'OR "weight loss"[Title] OR "weight management"[Title] '
    'OR "weight regain"[Title] OR bariatric[Title] OR semaglutide[Title] '
    'OR tirzepatide[Title] OR liraglutide[Title] OR "GLP-1"[Title] '
    'OR "body mass index"[Title] OR "metabolic syndrome"[Title])) '
    'NOT ("Artificial Intelligence"[Majr] OR "Machine Learning"[Majr] '
    'OR "Deep Learning"[Majr] OR "Telemedicine"[Majr] '
    'OR "Medical Informatics"[Majr] OR "Mobile Applications"[Majr] '
    'OR "Electronic Health Records"[Majr] '
    'OR "Nursing"[Majr] OR "Nursing Care"[Majr] OR "Long-Term Care"[Majr] '
    'OR "Nursing Homes"[Majr] OR "Caregivers"[Majr] '
    'OR "Aging"[Majr] OR "Longevity"[Majr] OR "Frailty"[Majr] '
    'OR "Geriatrics"[Majr] OR "Health Services for the Aged"[Majr] '
    'OR "Health Literacy"[Majr] OR "Patient Education as Topic"[Majr] '
    'OR "Climate Change"[Majr] OR "Air Pollution"[Majr] '
    'OR "Vaccination"[Majr] OR "Vaccines"[Majr] OR "Immunization"[Majr] '
    'OR "Noncommunicable Diseases"[Majr] OR "Multimorbidity"[Majr]))'
)
_KONTEXT = (
    '("Delivery of Health Care"[MeSH Terms] OR "Health Services"[MeSH Terms] '
    'OR "Quality of Health Care"[MeSH Terms] OR "Patient Care"[MeSH Terms] '
    'OR "Health Policy"[MeSH Terms] OR "Public Health"[MeSH Terms] '
    'OR "health care"[Title/Abstract] OR "health services"[Title/Abstract] '
    'OR "patient outcome*"[Title/Abstract] OR "clinical practice"[Title/Abstract] '
    'OR implementation[Title/Abstract] OR patients[Title/Abstract])'
)
# "Humans"[MeSH] haelt Tier-, Labor- und reine Modellarbeiten heraus.
TERM = os.environ.get(
    "SEARCH_TERM",
    f'(({_THEMA} AND {_KONTEXT}) AND "Humans"[MeSH Terms])',
)
# Zweite Abfrage, damit Arbeiten mit Deutschland- und Europabezug den
# Kandidatenpool sicher erreichen. Ueber MeSH und Autorenadresse, nicht ueber
# Journalnamen - deutschsprachige Journale liefern kaum Treffer.
TERM_DE = os.environ.get(
    "SEARCH_TERM_DE",
    f"{TERM} AND (Germany[MeSH Terms] OR Germany[Affiliation] "
    "OR Europe[MeSH Terms] OR Europe[Affiliation])",
)

# Groesse des Kandidatenpools. Europa steht vorn und stellt die Mehrheit -
# ein Sprachmodell gewichtet, was es zuerst liest. Wer das umdreht, bekommt
# eine Auswahl ohne Bezug zu hiesigen Verhaeltnissen; im Klima-Portal ist
# genau das passiert.
POOL_EUROPA = 30
POOL_ALLGEMEIN = 25
# Welche Abfrage vorn steht. True ist der Regelfall und die Lehre aus dem
# Klima-Portal: Steht die allgemeine Abfrage vorn, kommt eine Auswahl ohne
# Bezug zu hiesigen Verhaeltnissen heraus. Das Versorgungsforschungs-Portal
# arbeitet historisch andersherum (40 allgemein + 15 deutsch) - dort steht
# hier False, damit der Anschluss an die Vorlage nichts an seiner taeglichen
# Auswahl geaendert hat. Umstellen ist eine redaktionelle Entscheidung.
EUROPA_ZUERST = True

# Wie viele Studien taeglich erscheinen. SOLL wird im Prompt verlangt und beim
# Kappen verwendet; ueber MAX wird gekappt, unter MIN bricht der Lauf ab.
# **Nicht ins JSON-Schema schreiben** - die Anthropic-API lehnt minItems > 1
# und maxItems ab (am 17.08.2026 zweimal mit HTTP 400 belegt).
ANZAHL_SOLL = 6
ANZAHL_MAX = 7
ANZAHL_MIN = 1
# True: zu viele Studien werden auf ANZAHL_SOLL gekuerzt (die Auswahl ist nach
# Relevanz geordnet, die vorderen sind brauchbar). False: zu viele lassen den
# Lauf scheitern - so hielt es das Versorgungsforschungs-Portal von Anfang an.
KAPPEN = True

# ------------------------------------------------------------------- Prompts
SYSTEM = (
    "Du bist Fachredakteur fuer die Versorgung bei Adipositas. "
    "Aus einer Liste von PubMed-Abstracts waehlst du die relevantesten "
    "aktuellen Studien aus und fasst sie praezise auf Deutsch zusammen. "
    "Deine Leserschaft arbeitet im deutschen Gesundheitswesen: Praxen, "
    "Kliniken, Kostentraeger, Selbstverwaltung und Gesundheitspolitik. "
    "Sie will wissen, was Menschen mit Adipositas tatsaechlich erreicht - "
    "nicht, welches Praeparat im Studienarm die meisten Kilogramm senkte."
)

USER_TEMPLATE = """Unten stehen aktuelle PubMed-Abstracts (nach Datum sortiert).

Waehle GENAU 6 Studien aus, die (a) die Versorgung, Praevention oder Krankheitslast bei Adipositas untersuchen UND (b) im
Abstract ein BENENNBARES ERGEBNIS berichten. Bei quantitativen Arbeiten heisst
das: konkrete Zahlen (Prozentwerte, Effektstaerken, Odds/Hazard Ratios, Zeit-
oder Kostenwirkungen, Fallzahlen, p-Werte) - und die gehoeren dann auch in die
Zusammenfassung. Qualitative Studien (Interviews, Fokusgruppen) und
Expertenpapiere sind ausdruecklich zugelassen; bei ihnen tritt an die Stelle
der Zahl die klar benannte Kernaussage - welche Faktoren, welche Bedingungen,
welche Empfehlung. Was NICHT genuegt, ist ein Abstract, der nur ankuendigt,
was untersucht wurde, ohne zu sagen, was dabei herauskam.
Ueberspringe Studien ohne Abstract oder ohne benennbares Ergebnis. Achte auf
thematische Vielfalt und mische quantitative und qualitative Arbeiten.

THEMATISCHE RANGFOLGE - in dieser Reihenfolge bevorzugen:
  1. Versorgung und Ergebnis: Was veraendert den Verlauf? Programme,
     Koordination, Nachsorge, Zugang zur Behandlung - gemessen an
     Folgeerkrankungen, Krankenhauseinweisungen, Sterblichkeit,
     Funktionsfaehigkeit oder patientenberichteten Ergebnissen.
  2. Zugang und Erstattung: Wer bekommt eine Behandlung, wer nicht, und
     woran liegt es. Leistungsausschluesse, Wartezeiten, Selbstzahlung,
     regionale Unterschiede, Nutzenbewertungen. Das ist die Frage, die
     dieses Feld von der Ernaehrungsforschung unterscheidet.
  3. Praevention auf Bevoelkerungsebene: Kennzeichnung, Steuern,
     Werbebeschraenkungen, Schul- und Kitaverpflegung, Bewegungsfoerderung -
     jeweils mit gemessener Wirkung, nicht als Absichtserklaerung.
  4. Kinder und Jugendliche: Frueher Verlauf, Uebergang ins Erwachsenenalter,
     Familien- und Schulinterventionen. Hier entscheidet sich der
     Krankheitsverlauf Jahrzehnte im Voraus.
  5. Stigma und Ungleichheit: Wie Zuschreibungen den Zugang zur Versorgung
     veraendern und wie sich soziale Lage im Koerpergewicht niederschlaegt.
  6. Arzneimitteltherapie und Chirurgie nur mit einem Ergebnis, das ueber
     die Waage hinausgeht - Folgeerkrankungen, Lebensqualitaet, Kosten,
     Abbruchquoten, Gewichtsverlauf nach dem Absetzen.

NICHT in die Auswahl gehoeren:
Grundlagenforschung, Molekularbiologie und Tiermodelle, Studien zu einzelnen Naehrstoffen oder Nahrungsergaenzungsmitteln ohne Versorgungsbezug, Phase-I- und Phase-II-Studien, Validierungen von Messverfahren und Bildgebung ohne Ergebnisbezug, Fallberichte und Fallserien, reine Praevalenzmeldungen ohne Bezugsgroesse, Arbeiten, deren einziges Ergebnis eine Gewichtsdifferenz ueber wenige Wochen ist, sowie Uebersichten, die nichts Eigenes berichten.

HARTE REGELN ZUR ZUSAMMENSETZUNG (sie gehen der thematischen Rangfolge vor):
  1. MINDESTENS DREI der sechs Studien muessen aus Europa stammen oder ein
     europaeisches Gesundheitssystem betreffen. Liegen weniger als drei solche
     Arbeiten vor, nimm die verbleibenden Plaetze aus dem Rest - aber schoepfe
     die europaeischen zuerst aus.
  2. HOECHSTENS ZWEI der sechs duerfen eine Arzneimitteltherapie im Mittelpunkt
     haben (GLP-1-Rezeptoragonisten und andere Praeparate zur
     Gewichtsregulierung). Am 24.08.2026 machten sie 16,5 Prozent des
     Suchraums aus und wachsen schnell; ohne diese Grenze bestuende der Hub
     binnen Wochen aus Zulassungsstudien.
  3. HOECHSTENS EINE darf einen chirurgischen Eingriff im Mittelpunkt haben
     (16,7 Prozent des Suchraums). Die Adipositaschirurgie publiziert
     ueberproportional viel, betrifft aber einen kleinen Teil der Versorgten.
  4. HOECHSTENS EINE darf ausschliesslich Praevalenz, BMI-Verteilung oder
     Zeittrends berichten (20,8 Prozent des Suchraums). Solche Arbeiten sagen,
     wie gross das Problem ist, nicht, was hilft.
  5. HOECHSTENS EINE darf eine digitale Anwendung, eine App oder ein Verfahren
     des maschinellen Lernens im Mittelpunkt haben. Die Abfrage schliesst
     solche Arbeiten bereits aus, wenn sie dort das Hauptthema sind; diese
     Quote faengt die uebrigen. Sie gehoeren in das Schwesterportal ki.m-vf.de.

ZWEITES AUSWAHLKRITERIUM - Übertragbarkeit auf Deutschland:
Bei sonst gleicher Qualität hat die übertragbare Studie IMMER Vorrang vor der
aktuelleren.

  Hoch:    Deutschland und deutschsprachiger Raum, vergleichbare Sozial-
           versicherungssysteme.
  Mittel:  Übriges Europa, Kanada, Australien - andere Ausgangslage,
           ähnlicher Versorgungsauftrag.
  Gering:  USA und Länder mit grundlegend anderer Finanzierung oder
           Ressourcenlage. Nur nehmen, wenn die Fragestellung davon
           unabhängig ist.

Besonderheit dieses Themenfeldes: Bei Adipositas entscheidet nicht die Wirksamkeit darueber, was ankommt, sondern das Erstattungsrecht. In Deutschland schliesst Paragraf 34 SGB V Arzneimittel zur Gewichtsreduktion von der Leistungspflicht der gesetzlichen Krankenversicherung aus - eine Regelung, die kaum ein anderes Land in dieser Form kennt. Eine amerikanische Studie zu einem Praeparat, das dort von der Versicherung getragen wird, beschreibt deshalb eine Versorgung, die es hier nicht gibt. Massgeblich sind ausserdem: ob es strukturierte Programme gibt, wer die Adipositaschirurgie genehmigt (in Deutschland die Einzelfallpruefung der Kasse), und ob Adipositas als Krankheit anerkannt ist. Ordne die Systeme nach Vergleichbarkeit: hoch bei DACH, Niederlanden, Belgien und Frankreich, mittel bei Skandinavien, Grossbritannien, Kanada und Australien, gering bei den USA und bei Laendern mit ueberwiegend privater Finanzierung. Nenne im Feld transfer ausdruecklich, woran die Uebertragbarkeit haengt - bei Arzneimitteln und chirurgischen Eingriffen IMMER die Kostenuebernahme.

Fuer jede Studie:
- journal: Journalname genau so, wie er in der Kopfzeile des Abstracts steht -
  Abkuerzung nicht aufloesen, nichts ergaenzen. (Wird ohnehin durch die Angabe
  aus PubMed ersetzt; rate hier nichts.)
- year: Erscheinungsjahr, z. B. "2026"
- pmid: die PubMed-ID
- title: praegnanter deutscher Titel, **hoechstens 160 Zeichen**. Der
  Torwaechter lehnt alles ueber 200 Zeichen ab und stoppt damit die ganze
  Ausgabe - Methode und Population gehoeren nicht in den Titel, sie stehen
  in sum und transfer.
  **Er MUSS das Ergebnis nennen, nicht nur die Massnahme.** Und er darf sich
  NICHT auf die Kilogramm beschraenken: Eine Gewichtsdifferenz ist die
  Schlagzeile der Zulassungsstudie, nicht die Frage der Versorgungsforschung.
  Gesucht ist, was daraus folgte - fuer Folgeerkrankungen, Lebensqualitaet,
  Kosten, Zugang oder Verbleib in der Behandlung. Nicht "Adipositas bei
  Jugendlichen: eine Kohortenstudie", sondern "Strukturierte Nachsorge
  halbierte die Abbruchquote nach Magenbypass".
- sum: 1 Satz auf Deutsch, was die Studie untersucht hat. Wenn der genannte
  Anlassfall nur das Material ist, an dem gerechnet wurde, sage das
  ausdruecklich - sonst haelt die Leserschaft ihn fuer den Gegenstand.
- result: Deutsch, die konkreten Zahlen/Befunde + ein kurzer Einordnungssatz.
  Deutsches Zahlenformat mit Komma (z. B. 0,63). **Der Einordnungssatz darf
  nicht behaupten, was die Autoren selbst ablehnen.** Wo ein Abstract eine
  Deutung ausdruecklich zurueckweist, diese Einschraenkung uebernehmen statt
  sie zu ueberschreiben. Ein Rechercheportal referiert, es wertet nicht auf.
- transfer: EIN Halbsatz (höchstens 12 Wörter), warum das Ergebnis für Deutschland
  taugt - oder wo die Grenze liegt. Nenne Land bzw. System und Datengrundlage.
  Keine ganzen Sätze, keine Wiederholung des Titels.
  Gut:      "Deutsche Klinikdaten, vergleichbare Dokumentationspflichten"
            "Niederlande, vergleichbares Versicherungssystem"
            "USA - nur der Sicherheitsbefund ist übertragbar"
  Schlecht: "Diese Studie ist gut übertragbar." (sagt nichts)

WICHTIG - Fachterminologie: Etablierte englische Fachbegriffe NICHT eindeutschen.
Sie sind auch im deutschen Fachdeutsch stehende Begriffe; eine woertliche
Uebersetzung wirkt unprofessionell und erschwert das Wiederfinden.
Beispiele fuer Begriffe, die englisch bleiben: GLP-1, Set-Point, Sleeve, Binge Eating, Weight Bias, Food Environment, Patient-Reported Outcomes. Uebersetze dagegen, was im Deutschen eine gaengige Entsprechung hat: aus "bariatric surgery" wird die Adipositaschirurgie, aus "weight regain" die Wiederzunahme, aus "structural prevention" die Verhaeltnispraevention, aus "adherence" die Therapietreue.
Faustregel: Wuerde eine deutsche Fachzeitschrift wie Monitor Versorgungsforschung
den Begriff englisch stehen lassen, dann tue es auch. Im Zweifel englisch
belassen und bei Bedarf eine kurze deutsche Erlaeuterung in Klammern ergaenzen.

Gib ausschliesslich das geforderte JSON zurueck.

=== ABSTRACTS ===
{abstracts}
"""


# ------------------------------------------------- Newsfeed
# Wonach dieser Hub im MVF-Archiv sucht (scripts/newsfeed.py). Eigene Liste
# statt der Schnellwahlbegriffe: Chips sind fuer Datenbankabfragen gemacht und
# treffen im deutschen Archiv oft daneben - im Gender-Hub holten "Herzinfarkt"
# und "Arzneimittelsicherheit" allgemeine Herz- und Arzneimittelmeldungen, im
# Mental-Hub brachte "Wartezeit" jeden Arzttermin.
#
# Am 29.08.2026 gegen das Archiv gemessen; einzelne Begriffe stehen trotz
# heute null Treffern drin, weil sie fachlich in der Mitte des Themas liegen
# und das Archiv taeglich waechst. Ein Abruf ohne Treffer kostet nichts.
NEWS_SUCHE = [
    "Adipositas",
    "Adipositastherapie",
    "Übergewicht",
    "Abnehmspritze",
    "Verhältnisprävention",
    "Adipositaschirurgie",
]
