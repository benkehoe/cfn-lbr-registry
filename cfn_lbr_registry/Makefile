#Copyright 2018 iRobot Corporation
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

SHELL = /bin/bash
PYTHON := python$(PYTHON_VERSION)

$(if $(BUILD_DIR),,$(error BUILD_DIR required))
$(if $(CONFIG_FILE),,$(error CONFIG_FILE required))
$(if $(STACK_NAME),,$(error STACK_NAME required))

ARTIFACT_PREFIX ?= .lbr-registry-artifact-

TEMPLATE_FILE = $(ARTIFACT_PREFIX)template.yaml
PACKAGED_TEMPLATE_FILE = $(ARTIFACT_PREFIX)packaged-template.yaml

CODE_KEY_PREFIX = code
TEMPLATE_KEY_PREFIX = template

.DEFAULT_GOAL := all

LBR_FILE_NAME ?= lbr.yaml

LBR_CODE_URIS := $(shell $(PYTHON) -m "cfn_lbr_registry.config" paths $(CONFIG_FILE))
LBR_FILE_PATHS := $(addsuffix /$(LBR_FILE_NAME),$(LBR_CODE_URIS))

$(BUILD_DIR)/$(TEMPLATE_FILE): $(CONFIG_FILE) $(LBR_FILE_PATHS)
	@echo Generating template
	@mkdir -p $(BUILD_DIR) && $(PYTHON) -m "cfn_lbr_registry.config" template $(CONFIG_FILE) $(BUILD_DIR)/$(TEMPLATE_FILE)

.PHONY:
template: $(BUILD_DIR)/$(TEMPLATE_FILE)

REQUIRE_BUCKET = $(if $(BUCKET),,$(error BUCKET required))
.PHONY: require_bucket
require_bucket:
	$(REQUIRE_BUCKET)

$(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE): require_bucket $(BUILD_DIR)/$(TEMPLATE_FILE)
	@echo Packaging code
	@OUTPUT=$$(aws s3api head-bucket $(AWS_ARGS) --bucket $(BUCKET) 2>&1); \
	if [ -z "$$OUTPUT" ]; then \
	  true; \
	elif echo "$$OUTPUT" | grep -q "404"; then \
	  echo "Creating code bucket" && aws s3api create-bucket --bucket $(BUCKET); \
	else \
	  false; \
	fi
	@aws cloudformation package \
	$(AWS_ARGS) \
	--template-file $(BUILD_DIR)/$(TEMPLATE_FILE) \
	--s3-bucket $(BUCKET) \
	--s3-prefix $(CODE_KEY_PREFIX) \
	--output-template-file $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE) > /dev/null

.PHONY: package
package: $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE)

NO_CHANGES_REGEX := "\(No changes to deploy\)\|\(No updates are to be performed\)"

.PHONY: deploy
deploy: require_bucket $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE)
	@echo Deploying stack: $(STACK_NAME)
	@aws cloudformation deploy \
	$(AWS_ARGS) \
	--stack-name $(STACK_NAME) \
	--template-file $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE) \
	--s3-bucket $(BUCKET) \
	--s3-prefix $(CODE_KEY_PREFIX) \
	--capabilities CAPABILITY_IAM 2> $(BUILD_DIR)/deploy.err || \
	(sed -e '/^$$/d' $(BUILD_DIR)/deploy.err && \
	if grep -q $(NO_CHANGES_REGEX) $(BUILD_DIR)/deploy.err; then \
	  rm -f $(BUILD_DIR)/deploy.err; \
	else \
    rm -f $(BUILD_DIR)/deploy.err && false; \
	fi)


.PHONY: clean
clean:
	rm -f $(BUILD_DIR)/$(ARTIFACT_PREFIX)*

.PHONY: all
all: deploy
