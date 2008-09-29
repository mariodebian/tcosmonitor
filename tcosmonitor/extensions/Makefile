all:
	#none

include ../../common.mk


clean:
	rm -f *~ *.pyc

install:
	install -d $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/extensions
	@for ext in $(shell ls *.py |grep -v template); do \
		echo "install -m 644 $$ext $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/extensions" ; \
		install -m 644 $$ext $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/extensions ; \
	done
