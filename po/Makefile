LANGUAGES=es pt_BR ca ca@valencia gl

all: gmo


clean:
	@echo " **CLEAN**"
	@rm -rf *.mo *~ tmp/
	@for lang in $(LANGUAGES); do \
		echo " **CLEANDIR** $$lang"; \
		rm -rf $$lang;\
	done

files:
#	find ../ -name "*.ui" -o -name "*.py" | grep -v WakeOnLan > FILES

pot:
	find ../ -name "*.ui" | grep -v WakeOnLan > FILES.ui.txt
	find ../ -name "*.py" | grep -v WakeOnLan > FILES.py.txt
#	xgettext --add-comments -o tcosmonitor.pot --files-from=FILES
	xgettext -o tcosmonitor.py.pot --files-from=FILES.py.txt --language=Python
	xgettext -o tcosmonitor.ui.pot --files-from=FILES.ui.txt --language=Glade
	msgcat -o tcosmonitor.pot tcosmonitor.py.pot tcosmonitor.ui.pot
	rm -f tcosmonitor.py.pot tcosmonitor.ui.pot FILES.ui.txt FILES.py.txt

po:
	@for lang in $(LANGUAGES); do \
		echo " **PO** $$lang"; \
		if [ ! -f $$lang.po ]; then \
			msginit --input tcosmonitor.pot -o $$lang-old.po;\
		else \
			mv $$lang.po $$lang-old.po; \
		fi ; \
		msgmerge -o $$lang.po $$lang-old.po tcosmonitor.pot; \
		rm -f $$lang-old.po; \
	done

gmo:
	@echo " **COMPILING** languages: $(LANGUAGES)"
	@for lang in $(LANGUAGES); do \
		echo " **COMPILEMO** $$lang" ; \
		mkdir -p $$lang/LC_MESSAGES/; \
		msgfmt --verbose -o $$lang/LC_MESSAGES/tcosmonitor.mo $$lang.po; \
	done
	
install:
	@echo " **INSTALL** languages: $(LANGUAGES)"
	@for lang in $(LANGUAGES); do \
		echo " **INSTALLMO** $$lang" ; \
		mkdir -p $(DESTDIR)/usr/share/locale/$$lang/LC_MESSAGES/; \
		msgfmt -o $(DESTDIR)/usr/share/locale/$$lang/LC_MESSAGES/tcosmonitor.mo $$lang.po; \
	done
	
