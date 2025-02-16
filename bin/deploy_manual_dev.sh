# Incluir funciones comunes
source bin/commons/common_functions.sh

# Habilitar modo estricto y debugging
set -euo pipefail


#set -x
IFS=$'\n\t'

# VARIABLES ESTANDAR
AWS_ACCOUNT="apps"
AWS_PROFILE="default"  
AWS_REGION="us-east-1"
SOURCE="$(pwd)"
SOURCE_BUILDED="$(pwd)/.aws-sam/build"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UUID=$$
SAM_PATH="$SAM_PATH\sam.cmd"

## Cuenta AWS APP-DEV
BUCKET="spv-dev-srvless-deploy"
STACK="srvless-cursos-api-poc"

# Datos de la aplicación
pEnv="dev"
pOwner="legales-reciprocidad"
pAppName=cursos
pLambdaName=curso
pProduct="cursos-api"

# Datos extras
pTechVersion='python3.12'
pCostCenterTag=0751

#----------------------------- Zona de funciones -----------------------------#
# Validar parámetros necesarios para el despliegue
validate_parameters() {
    local missing_params=()
    
    # Lista de parámetros obligatorios
    local required_params=( "AWS_ACCOUNT" "AWS_REGION" "AWS_PROFILE" "BUCKET" "STACK" "pEnv" "pAppName" "pLambdaName" "pTechVersion" "pCostCenterTag" "pBuildVersion")

    # Validar si existen y no están vacíos
    for param in "${required_params[@]}"; do
        if [ -z "${!param:-}" ]; then
            missing_params+=("$param")
        fi
    done

    if [ ${#missing_params[@]} -gt 0 ]; then
        print_message "$RED" "❌ Faltan los siguientes parámetros obligatorios: ${missing_params[*]}${NC}"
        exit 1
    fi
    print_message "$GREEN" "✅ Todos los parámetros obligatorios están presentes.${NC}"
}

# Construir parámetros para SAM deploy
build_parameter_overrides() {
    local parameter_overrides=()

    parameter_overrides+=("pAccount=$AWS_ACCOUNT")
    parameter_overrides+=("pEnvironment=$pEnv")
    parameter_overrides+=("pAppName=$pAppName")
    parameter_overrides+=("pLambdaName=$pLambdaName")
    parameter_overrides+=("pTechVersion=$pTechVersion")
    parameter_overrides+=("pCostCenterTag=$pCostCenterTag")
    parameter_overrides+=("pBuildVersion=$pBuildVersion")    

    # Unir parámetros con espacios (si es necesario)
    echo "${parameter_overrides[*]}"
}

copy_definition_file() {
    local source_file="$PROJECT_ROOT/docs/swagger-cursos-api.yaml"
    local destination_file_api="$SOURCE_BUILDED/swagger-cursos-api.yaml"
    local destination_file_lambda="$SOURCE_BUILDED/SwaggerFunction/swagger-cursos-api.yaml"

    echo "📂 Copiando el archivo Swagger..."
    echo "📌 Archivo origen: $source_file"

    # Verifica que el archivo exista
    if [ ! -f "$source_file" ]; then
        print_message "$RED" "❌ El archivo de definición Swagger no existe en: $source_file${NC}"
        exit 1
    fi

    # Esperar a que SAM cree las carpetas necesarias después del build
    while [ ! -d "$SOURCE_BUILDED/SwaggerFunction" ]; do
        echo "⏳ Esperando a que SAM cree el directorio SwaggerFunction..."
        sleep 2
    done

    # Copia el archivo al destino para API Gateway
    cp "$source_file" "$destination_file_api"
    print_message "$GREEN" "✅ Archivo Swagger copiado a API Gateway: $destination_file_api${NC}"

    # Copia el archivo al destino para la Lambda
    cp "$source_file" "$destination_file_lambda"
    print_message "$GREEN" "✅ Archivo Swagger copiado a Lambda: $destination_file_lambda${NC}"
}

copy_definition_file_swagger_json() {
    local source_file="$PROJECT_ROOT/docs/swagger-cursos-api.json"
    local destination_file_lambda="$SOURCE_BUILDED/SwaggerFunction/swagger-cursos-api.json"
    
    echo "📂 Copiando el archivo Swagger..."
    echo "📌 Archivo origen: $source_file"

    # Verifica que el archivo exista
    if [ ! -f "$source_file" ]; then
        print_message "$RED" "❌ El archivo de definición Swagger no existe en: $source_file${NC}"
        exit 1
    fi

    # Esperar a que SAM cree las carpetas necesarias después del build
    while [ ! -d "$SOURCE_BUILDED/SwaggerFunction" ]; do
        echo "⏳ Esperando a que SAM cree el directorio SwaggerFunction..."
        sleep 2
    done

    # Copia el archivo al destino para la Lambda
    cp "$source_file" "$destination_file_lambda"
    print_message "$GREEN" "✅ Archivo Swagger copiado a Lambda: $destination_file_lambda${NC}"
}   

validate_swagger_file_in_build() {
    local swagger_file="$SOURCE_BUILDED/swagger-cursos-api.yaml"

    if [ ! -f "$swagger_file" ]; then
        print_message "$RED" "❌ El archivo Swagger no existe en la carpeta build: $swagger_file${NC}"
        exit 1
    else
        print_message "$GREEN" "✅ El archivo Swagger existe en la carpeta build.${NC}"
    fi
}

fix_definition_uri_in_template() {
    local template_file="$SOURCE_BUILDED/template.yaml"
    local corrected_uri="./swagger-cursos-api.yaml"

    echo "Corrigiendo DefinitionUri en $template_file..."

    if [ -f "$template_file" ]; then
        # Usar un delimitador alternativo para evitar conflictos con '/'
        sed -i "s|..\\\\..\\\\swagger-cursos-api.yaml|$corrected_uri|g" "$template_file"
        print_message "$GREEN" "✅ DefinitionUri corregido exitosamente en $template_file.${NC}"
    else
        print_message "$RED" "❌ No se encontró el archivo template.yaml en: $template_file${NC}"
        exit 1
    fi
}

main() {
    measure_time print_banner_init "AWS"
    measure_time read_build_version
    measure_time validate_aws_token
    measure_time validate_template_sam
    # 🏗️ Construcción del Proyecto
    measure_time build_stack
    #⏳ Copiar el archivo Swagger para API Gateway y Lambda después del build
    measure_time copy_definition_file_swagger_json
    #measure_time validate_swagger_file_in_build
    measure_time fix_definition_uri_in_template
    #measure_time validate_template_sam_build
    #cat "$SOURCE_BUILDED/template.yaml" | grep "DefinitionUri"
    measure_time package_stack
    # 🚀 Desplegar la API
    measure_time deploy_stack "$(build_parameter_overrides)" false
    # measure_time check_stack_status "$STACK" # Para usar con aws
    # measure_time check_stack_status "$STACK" true # Para usar con localstack
    measure_time cleanup 
    measure_time print_banner_fin "AWS"    
    generate_report
}
#----------------------------- FIN Zona de funciones -----------------------------#

#----------------------------- Inicio proceso ------------------------------------#
# Medir el tiempo total de ejecución del script
measure_total_time main

#----------------------------- FIN Inicio proceso --------------------------------#