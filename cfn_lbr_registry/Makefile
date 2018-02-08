SHELL = /bin/bash
BUILD_DIR = .
#TODO: change to ./.build and use --base-dir once available

ARTIFACT_PREFIX = lbr-registry-artifact-

TEMPLATE_FILE = $(ARTIFACT_PREFIX)template.yaml
PACKAGED_TEMPLATE_FILE = $(ARTIFACT_PREFIX)packaged-template.yaml

CONFIG_FILE=lbr-registry.yaml

ifndef STACK_NAME
  #TODO: check lbr-registry.yaml
  STACK_NAME=LBR-Registry
endif

ifndef ACCOUNT
  ACCOUNT:=$(shell aws sts get-caller-identity --query Account | tr -d \")
endif

ifndef REGION
  REGION:=$(shell aws configure list | awk '/region/{ print $$2 }')
endif

BUCKET=lbr-registry-$(ACCOUNT)-$(REGION)
CODE_KEY_PREFIX=code
TEMPLATE_KEY_PREFIX=template

.DEFAULT_GOAL := all

$(BUILD_DIR)/$(TEMPLATE_FILE): $(CONFIG_FILE)
	@echo Generating template
	@mkdir -p $(BUILD_DIR) && python$(LBR_PYTHON_VERSION) -m "cfn_lbr_registry.config" $(CONFIG_FILE) $(BUILD_DIR)/$(TEMPLATE_FILE)

.PHONY:
template: $(BUILD_DIR)/$(TEMPLATE_FILE)

$(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE): $(BUILD_DIR)/$(TEMPLATE_FILE)
	@echo Packaging code
	@OUTPUT=$$(aws s3api head-bucket --bucket $(BUCKET) 2>&1); \
	if [ -z "$$OUTPUT" ]; then \
	  true; \
	elif echo "$$OUTPUT" | grep -q "404"; then \
	  echo "Creating code bucket" && aws s3api create-bucket --bucket $(BUCKET) --create-bucket-configuration LocationConstraint=$(REGION); \
	else \
	  false; \
	fi
	@aws cloudformation package \
	--template-file $(BUILD_DIR)/$(TEMPLATE_FILE) \
	--s3-bucket $(BUCKET) \
	--s3-prefix $(CODE_KEY_PREFIX) \
	--output-template-file $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE) > /dev/null

.PHONY: package
package: $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE)

NO_CHANGES_REGEX := "\(No changes to deploy\)\|\(No updates are to be performed\)"

.PHONY: deploy
deploy: $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE)
	@echo Deploying stack: $(STACK_NAME)
	@aws cloudformation deploy \
	--stack-name $(STACK_NAME) \
	--template-file $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE) \
	--s3-bucket $(BUCKET) \
	--s3-prefix $(CODE_KEY_PREFIX) \
	--capabilities CAPABILITY_IAM 2> $(BUILD_DIR)/deploy.err || \
	sed -e '/^$$/d' $(BUILD_DIR)/deploy.err && \
	if grep -q $(NO_CHANGES_REGEX) $(BUILD_DIR)/deploy.err; then \
	  rm -f $(BUILD_DIR)/deploy.err; \
	else \
	  rm -f $(BUILD_DIR)/deploy.err && false; \
	fi


.PHONY: clean
clean:
	rm -f $(BUILD_DIR)/$(ARTIFACT_PREFIX)*

.PHONY: all
all: deploy
