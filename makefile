CMD_VENV		:=	virtualenv
DIR_VENV		:=	venv
VER_PY			:=	3.9

CMD_ISORT		:=	$(DIR_VENV)/bin/isort
CMD_PIP			:=	$(DIR_VENV)/bin/pip$(VER_PY)
CMD_PYTHON3		:=	$(DIR_VENV)/bin/python$(VER_PY)
CMD_PYLINT		:=	$(DIR_VENV)/bin/pylint

DIR_SITE		:=	$(DIR_VENV)/lib/python$(VER_PY)/site-packages
LIB_CLICK		:=	$(DIR_SITE)/click/__init__.py
LIB_ICS			:=	$(DIR_SITE)/ics/__init__.py
LIB_REQUESTS	:=	$(DIR_SITE)/requests/__init__.py
CMD_PUDB		:=	$(DIR_VENV)/bin/pudb


SCR_TRASHPLAN	:=	trashplan.py


.PHONY: help
help:
	@echo "trashplan makefile"
	@echo "------------------"
	@echo
	@echo "requirements         install requirements"
	@echo "requirements-dev     install requirements for developing"
	@echo
	@echo "sort                 run $(CMD_ISORT) on $(SCR_TRASHPLAN)"
	@echo "lint                 run $(CMD_PYLINT) on $(SCR_TRASHPLAN)"


$(DIR_VENV):
	$(CMD_VENV) -p "python$(VER_PY)" "$(DIR_VENV)"
	$(CMD_PIP) install -U pip

$(LIB_CLICK) $(LIB_ICS) $(LIB_REQUESTS): $(DIR_VENV)
	$(CMD_PIP) install -r "requirements.txt"

$(CMD_ISORT) $(CMD_PYLINT): $(DIR_VENV)
	$(CMD_PIP) install -r "requirements-dev.txt"

$(CMD_PUDB): $(DIR_VENV)
	$(CMD_PIP) install -r "requirements-dbg.txt"

.PHONY: requirements
requirements: $(LIB_CLICK) $(LIB_ICS) $(LIB_REQUESTS)

.PHONY: requirements-dev
requirements-dev: $(CMD_ISORT) $(CMD_PYLINT)

.PHONY: requirements-dbg
requirements-dbg: $(CMD_PUDB)


define _sort
	$(CMD_ISORT) \
		--combine-star \
		--force-sort-within-sections \
		--py "$(subst .,,$(VER_PY))" \
		--line-width="79" \
		--multi-line "VERTICAL_HANGING_INDENT" \
		--trailing-comma \
		--force-grid-wrap 0 \
		--use-parentheses \
		--ensure-newline-before-comments \
			$(1)
endef

.PHONY: sort
sort: requirements-dev
	$(call _sort,"$(SCR_TRASHPLAN)")


define PYLINT_MESSAGE_TEMPLATE
{C} {path}:{line}:{column} - {msg}
  ↪  {category} {module}.{obj} ({symbol} {msg_id})
endef
export PYLINT_MESSAGE_TEMPLATE

define _lint
	$(CMD_PYLINT) \
		--disable "C0111" \
		--msg-template="$$PYLINT_MESSAGE_TEMPLATE" \
		--output-format="colorized" \
			$(1)
endef

.PHONY: lint
lint: requirements-dev
	$(call _lint,"$(SCR_TRASHPLAN)")



NHR_NOS				:=	13486	# Martin-Luther-Ring 4 - 6

neues-rathaus: requirements
	$(CMD_PYTHON3) $(SCR_TRASHPLAN) "$(NHR_NOS)" \
		--only-future
