.PHONY: help preview render sync-aboutme sync-notes clean check

# Load repo-local .env (e.g. OBSIDIAN_VAULT_NOTES) and export to recipes.
-include .env
export

help:
	@echo "Targets:"
	@echo "  make preview       Render once, then start the live preview server"
	@echo "  make render        Build the site to _site/ and exit"
	@echo "  make sync-aboutme  Fetch the GitHub profile README, then clean + render"
	@echo "  make sync-notes    Mirror \$$OBSIDIAN_VAULT_NOTES into notes/, then clean + render"
	@echo "  make clean         Remove build outputs (_site/, .quarto/)"
	@echo "  make check         Run quarto check for environment diagnostics"

# Pulls the profile README, busts Quarto's incremental cache so the
# {{< include >}}'d about-me changes take effect, then re-renders.
sync-aboutme: clean
	./scripts/fetch-aboutme.sh
	$(MAKE) render

# Pulls notes from Obsidian, busts Quarto's incremental cache so sidebar
# changes (new sections, edited titles) take effect, then re-renders.
sync-notes: clean
	./scripts/sync_notes.py
	$(MAKE) render

preview:
	./scripts/sync_notes.py
	quarto preview

render:
	./scripts/sync_notes.py
	quarto render

clean:
	rm -rf _site .quarto

check:
	quarto check
