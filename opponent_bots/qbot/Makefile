JAVAC=javac
JAVAC_ARGS=

SOURCES=Ants.java Bot.java Aim.java Ilk.java Order.java Tile.java AbstractSystemInputParser.java AbstractSystemInputReader.java MyBot.java
CLASSES=$(addsuffix .class, $(basename ${SOURCES}))
JAR=MyBot.jar

.PHONY: all clean zip

all: $(CLASSES) $(JAR)

$(JAR): $(CLASSES)
	jar cvfm $(JAR) Manifest.txt *.class

%.class: %.java
	$(JAVAC) $(JAVAC_ARGS) $<

clean:
	-rm -Rf $(CLASSES)
	-rm -Rf *.class
	-rm -Rf $(JAR)

zip:
	zip QBot.zip *.java Makefile make.cmd Manifest.txt VERSION

