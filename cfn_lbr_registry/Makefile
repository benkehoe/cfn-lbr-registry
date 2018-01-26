SHELL = /bin/bash
BUILD_DIR = .

TEMPLATE_FILE = lbr-template.yaml
PACKAGED_TEMPLATE_FILE = lbr-packaged-template.yaml

STACK_NAME=LBR

CONFIG_FILE=lbr.yaml

ACCOUNT:=$(shell aws sts get-caller-identity --query Account | tr -d \")
REGION:=$(shell aws configure list | awk '/region/{ print $$2 }')

BUCKET=$(REGION).$(ACCOUNT).lbr
CODE_KEY_PREFIX=code

.DEFAULT_GOAL := all

$(BUILD_DIR)/$(TEMPLATE_FILE): $(CONFIG_FILE)
	@echo Generating template
	@mkdir -p $(BUILD_DIR) && python$(LBR_PYTHON_VERSION) -m "cfn_lbr_registry.config" $(CONFIG_FILE) $(BUILD_DIR)/$(TEMPLATE_FILE)

.PHONY:
template: $(BUILD_DIR)/$(TEMPLATE_FILE)

$(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE): $(BUILD_DIR)/$(TEMPLATE_FILE)
	@echo Packaging code
	@OUTPUT=$$(aws s3api head-bucket --bucket $(BUCKET) 2>&1); \
	if [ -z "$$OUTPUT" ]; then
	  true; \
	elif echo "$$OUTPUT" | grep -q "404"; then \
	  echo "Creating code bucket" && aws s3api create-bucket --bucket $(BUCKET) --create-bucket-configuration LocationConstraint=$(REGION); \
	else
	  false;
	fi
	@aws cloudformation package \
	--template-file $(BUILD_DIR)/$(TEMPLATE_FILE) \
	--s3-bucket $(BUCKET) \
	--s3-prefix $(CODE_KEY_PREFIX) \
	--output-template-file $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE) > /dev/null

.PHONY: package
package: $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE)

.PHONY: deploy
deploy: $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE)
	@echo Deploying stack: $(STACK_NAME)
	@aws cloudformation deploy \
	--template-file $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE) \
    --stack-name $(STACK_NAME) \
    --capabilities CAPABILITY_IAM 2> $(BUILD_DIR)/deploy.err || \
    sed -e '/^$$/d' $(BUILD_DIR)/deploy.err && \
    if grep -q "No changes to deploy" $(BUILD_DIR)/deploy.err; then \
      rm -f $(BUILD_DIR)/deploy.err; \
    else \
      rm -f $(BUILD_DIR)/deploy.err && false; \
    fi


.PHONY: clean
clean:
	rm -f $(BUILD_DIR)/$(TEMPLATE_FILE) $(BUILD_DIR)/$(PACKAGED_TEMPLATE_FILE)

.PHONY: all
all: deploy
