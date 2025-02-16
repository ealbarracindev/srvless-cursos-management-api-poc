#!/bin/bash
#----------------------------- Zona de funciones -----------------------------#
# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m' # Sin color

declare -A stage_times
total_time=0

# Función para imprimir mensajes coloreados
print_message() {
    local color=$1
    local message=$2
    local NC='\033[0m'  # Sin color
    echo -e "${color}${message}${NC}"
}

# Banner inicio
print_banner_init() {
    local environment=$1
    echo -e "${BLUE}"
    echo "###############################################"
    echo "      🚀 Bienvenidos al Despliegue en $environment! 🚀 "
    echo "           Inicio del proceso...               "
    echo "                                               "
    echo "###############################################"
    echo -e "${NC}"
}

# Banner fin
print_banner_fin() {
    local environment=$1
    echo -e "${GREEN}"
    echo "###############################################"
    echo "      🚀 Fin Despliegue en $environment! 🚀 "
    echo "        📢 Proceso exitoso 🎉!       "
    echo "             Version: $pBuildVersion            "
    echo "###############################################"
    echo -e "${NC}"
}

# Función para convertir cadena a minúsculas
to_lowercase() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

# Medir tiempo de ejecución de una función
measure_time() {
    local stage_name=$1
    shift  # Elimina el primer argumento (nombre de la etapa)
    local start_time=$(date +%s)

    echo "⏳ Iniciando la etapa: $stage_name"
    $stage_name "$@"  # Ejecuta la etapa con los argumentos restantes

    local end_time=$(date +%s)
    local elapsed_time=$((end_time - start_time))
    stage_times["$stage_name"]=$elapsed_time  # Registra el tiempo de la etapa
    total_time=$((total_time + elapsed_time))  # Suma al tiempo total

    echo "✅ Finalizó la etapa: $stage_name en ${elapsed_time} segundos"
}

# Función para medir el tiempo total de ejecución del script
measure_total_time() {
    local start_time=$(date +%s)

    # Ejecutar el script principal
    "$@"

    local end_time=$(date +%s)
    local elapsed_time=$((end_time - start_time))
    echo "⏱️ Tiempo total de ejecución: ${elapsed_time} segundos"
}

generate_report() {
    echo ""
    echo "📊 Reporte de tiempos de despliegue:"
    echo "------------------------------------"
    for stage in "${!stage_times[@]}"; do
        printf "⏱️  %s: %s segundos\n" "$stage" "${stage_times[$stage]}"
    done
    echo "------------------------------------"
    echo "⏱️  Tiempo total: $total_time segundos"
}

# Función para validar el token de AWS
validate_aws_token() {
    echo "Validando el token de AWS..."
    if aws sts get-caller-identity > /dev/null 2>&1; then
        print_message "$GREEN" "✅ El token de AWS está correcto.${NC}"
    else
        print_message "$RED" "❌ El token de AWS ha expirado o no es válido. Por favor, renueva tu sesión de AWS.${NC}"
        exit 1
    fi
}

# Función para obtener información de Git
get_git_info() {
    REPO_NAME=$(basename -s .git "$(git config --get remote.origin.url)")
    BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
    DOCKER_IMAGE=$(to_lowercase "$REPO_NAME")
    CONTAINER_NAME=$(to_lowercase "${REPO_NAME}-${BRANCH_NAME}")
    echo ""
    print_message "$YELLOW" "Repo: $REPO_NAME, Branch: $BRANCH_NAME."
}

# Validar el template con SAM
validate_template_sam() {
    local template_file=$1
    if ! sam validate --template "$template_file" --profile "$AWS_PROFILE"; then
        print_message "\033[0;31m" "❌ Error en la validación del template con SAM."
        exit 1
    fi
    print_message "\033[0;32m" "✅ Template validado exitosamente con SAM."
}

# Función para leer la versión de build desde el archivo build.version
read_build_version() {
    BUILD_VERSION_FILE="build.version"

    if [ ! -f "$BUILD_VERSION_FILE" ]; then
        echo -e "${RED}❌ Error: El archivo build.version no existe en la ruta especificada."
        exit 1
    fi

    pBuildVersion=$(cat "$BUILD_VERSION_FILE")

    if [ -z "$pBuildVersion" ]; then
        echo -e "${RED}❌ Error: No se pudo leer el valor del archivo build.version"
        exit 1
    fi
}

validate_template_sam() {
    echo "Validando el template con SAM..."
    if ! "$SAM_PATH" validate --lint --template "$SOURCE/template.yaml" --profile "$AWS_PROFILE"; then
        print_message "$RED" "❌ Error en la validación del template con SAM.${NC}"
        exit 1
    fi
    print_message "$GREEN" "✅ Template validado exitosamente con SAM.${NC}"
}

validate_template_sam_build() {
    echo "Validando el template con SAM generado en etapa BUILD..."
    if ! "$SAM_PATH" validate --lint --template "$SOURCE_BUILDED/template.yaml" --profile "$AWS_PROFILE"; then
        print_message "$RED" "❌ Error en la validación del template con SAM.${NC}"
        exit 1
    fi
    print_message "$GREEN" "✅ Template validado exitosamente con SAM.${NC}"
}

# Función para validar el template con cfn-lint
validate_template_lint() {
    local template_file=$1
    echo "Validando el template con cfn-lint..."
    if ! cfn-lint "$template_file"; then
        print_message "$RED" "❌ Error en la validación del template con cfn-lint.${NC}"
        exit 1
    fi
    print_message "$GREEN" "✅ Template validado exitosamente con cfn-lint.${NC}"
}

# Función para limpiar archivos temporales
cleanup() {
    echo "Limpiando archivos temporales..."
    rm -f "template_$UUID.yaml"
    print_message "$GREEN" "✅ Limpieza completada.${NC}"
}

# Función para verificar o crear el bucket S3
validate_or_create_s3_bucket() {
    local use_localstack=${2:-false}
    local endpoint_url=""
    
    if [ "$use_localstack" = true ]; then
        endpoint_url="--endpoint-url http://localhost:4566"
    fi
    
    if aws s3api  head-bucket --bucket "$BUCKET" $endpoint_url 2>/dev/null; then
        echo ""
        print_message "$GREEN" "El bucket S3 '$BUCKET' ya existe.${NC}"
    else
        echo ""
        print_message "$BLUE" "Creando el bucket S3 '$BUCKET'...${NC}"
        aws s3api  create-bucket \
            --bucket "$BUCKET" \
            --region "$AWS_REGION" \
            $endpoint_url 
        echo ""
        print_message "$GREEN" "Bucket '$BUCKET' creado con éxito.${NC}"
    fi
}

# Función para verificar el estado de la pila
check_stack_status() {
    local stack_name=$1
    local use_localstack=${2:-false}
    local stack_status
    local endpoint_url=""

    if [ "$use_localstack" = true ]; then
        endpoint_url="--endpoint-url http://localhost:4566"
    fi

    echo "Verificando el estado de la pila '$stack_name'..."
    stack_status=$(aws cloudformation describe-stacks \
        --stack-name "$stack_name" \
        --query "Stacks[0].StackStatus" \
        --output text $endpoint_url)

    if [[ "$stack_status" == "CREATE_COMPLETE" || "$stack_status" == "UPDATE_COMPLETE" ]]; then
        print_message "$GREEN" "📢 Despliegue exitoso. Estado de la pila: $stack_status${NC}"
    else
        print_message "$RED" "❌ Error en el despliegue. Estado de la pila: $stack_status${NC}"
        exit 1
    fi
}

# Función para construir la pila
build_stack() {
    local use_localstack=${1:-false}
    local endpoint_url=""

    if [ "$use_localstack" = true ]; then
        endpoint_url="--endpoint-url http://localhost:4566"
    fi

    status=0  # Inicializar variable

    "$SAM_PATH" build \
        --region "$AWS_REGION" \
        --template "$SOURCE/template.yaml" \
        --profile $AWS_PROFILE \
        --cached $endpoint_url
    
    status=$?
    if [ $status -ne 0 ]; then
        echo ""
        print_message "$RED" "❌ SAM build failed. Código: $status${NC}"
        exit 1
    else
        print_message "$GREEN" "✅ Build exitoso.${NC}"
        cd .aws-sam/build/
    fi    
}

# Función para empaquetar la pila
package_stack() {
    local use_localstack=${1:-false}
    local endpoint_url=""

    if [ "$use_localstack" = true ]; then
        endpoint_url="--endpoint-url http://localhost:4566"
    fi

    echo "Empaquetando la aplicación con SAM..."
    if ! "$SAM_PATH" package \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --template-file "$SOURCE_BUILDED/template.yaml" \
        --output-template-file "template_$UUID.yaml" \
        --s3-bucket "$BUCKET" $endpoint_url; then
        print_message "$RED" "❌ Error en el empaquetado.${NC}"
        exit 1
    fi
    print_message "$GREEN" "✅ Paquete generado exitosamente.${NC}"
}

# Actualizar función deploy_stack para validar parámetros
deploy_stack() {
    local parameter_overrides
    parameter_overrides=$(build_parameter_overrides)

    local use_localstack=${2:-false}
    local endpoint_url=""

    if [ "$use_localstack" = true ]; then
        endpoint_url="--endpoint-url http://localhost:4566"
    fi

    # Validar parámetros antes de ejecutar SAM deploy
    validate_parameters

    print_message "$BLUE" "Desplegando la aplicación con SAM..."
    print_message "$YELLOW" "Parámetros: $parameter_overrides"

    if ! "$SAM_PATH" deploy \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --template-file "template_$UUID.yaml" \
        --stack-name "$STACK" \
        --tags Environment="$pEnv" ProductName="$pProduct" Owner="$pOwner" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --parameter-overrides $parameter_overrides \
        --no-fail-on-empty-changeset $endpoint_url; then
        print_message "$RED" "❌ Error en el despliegue.${NC}"
        exit 1
    fi
    print_message "$GREEN" "✅ Despliegue exitoso.${NC}"
}