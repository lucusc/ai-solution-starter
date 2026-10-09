#!/bin/bash

deploy_component="$1"

if [ -z "$deploy_component" ]; then
    deploy_component="all"
    echo "No component specified. Defaulting to 'all'."
fi

if [ "$deploy_component" != "backend" ] && [ "$deploy_component" != "agent" ] && [ "$deploy_component" != "all" ]; then
    echo "Invalid component: $deploy_component"
    echo "Available components: backend, agent, all"
    exit 1
fi

resource_group=$(azd env get-value AZURE_RESOURCE_GROUP)
acr_name=$(azd env get-value AZURE_CONTAINER_REGISTRY_ENDPOINT)

if [ "$deploy_component" == "backend" ] || [ "$deploy_component" == "all" ]; then
    echo "Deploying backend..."

    backend_name=$(azd env get-value AZURE_BACKEND_SERVICE_NAME)
    backend_image_name="backend"

    . ./app/backend/docker-build.sh "$resource_group" "$acr_name" "$backend_name" "$backend_image_name"
fi

if [ "$deploy_component" == "agent" ] || [ "$deploy_component" == "all" ]; then
    echo "Deploying agent..."

    agent_name=$(azd env get-value AZURE_LOGICAPP_SERVICE_NAME)

    . ./app/agent/deploy.sh "$resource_group" "$agent_name"
fi

echo "Done."
