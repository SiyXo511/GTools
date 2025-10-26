#!/bin/bash

# GTools Docker启动脚本

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting GTools with Docker...${NC}"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# 选择运行模式
if [ "$1" == "prod" ]; then
    echo -e "${GREEN}Starting production environment...${NC}"
    docker-compose up -d gtools-prod
    echo -e "${GREEN}Production environment started at http://localhost:5000${NC}"
    echo "View logs: docker-compose logs -f gtools-prod"
elif [ "$1" == "dev" ]; then
    echo -e "${GREEN}Starting development environment...${NC}"
    docker-compose up -d gtools-dev
    echo -e "${GREEN}Development environment started at http://localhost:5000${NC}"
    echo "View logs: docker-compose logs -f gtools-dev"
else
    echo "Usage: ./docker-start.sh [dev|prod]"
    echo ""
    echo "Available modes:"
    echo "  dev  - Start development environment"
    echo "  prod - Start production environment"
    exit 1
fi
