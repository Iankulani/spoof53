#!/bin/bash
# Docker Quick Start Script for SPOOF53

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${GREEN}               SPOOF53 - Docker Quick Start                  ${BLUE}║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo -e "${YELLOW}Please install Docker first:${NC}"
    echo "  curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  docker-compose not found, using docker run instead${NC}"
    USE_COMPOSE=false
else
    USE_COMPOSE=true
fi

# Create directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p reports whatsapp_session signal_session logs ssh_keys

# Build and run
if [ "$USE_COMPOSE" = true ]; then
    echo -e "${BLUE}🐳 Using docker-compose...${NC}"
    docker-compose up -d --build
    echo -e "${GREEN}✅ SPOOF53 is running in Docker${NC}"
    echo -e "${BLUE}📊 View logs: docker-compose logs -f spoof53${NC}"
else
    echo -e "${BLUE}🐳 Building Docker image...${NC}"
    docker build -t spoof53:latest .
    
    echo -e "${BLUE}🚀 Running SPOOF53 container...${NC}"
    docker run -d \
        --name spoof53 \
        --privileged \
        --network host \
        -v $(pwd)/reports:/home/spoof53/spoof53_reports \
        -v $(pwd)/whatsapp_session:/home/spoof53/.spoof53/whatsapp_session \
        -v $(pwd)/signal_session:/home/spoof53/.spoof53/signal_session \
        -v $(pwd)/logs:/home/spoof53/.spoof53/logs \
        -v $(pwd)/ssh_keys:/home/spoof53/.spoof53/ssh_keys \
        spoof53:latest
    
    echo -e "${GREEN}✅ SPOOF53 is running in Docker${NC}"
    echo -e "${BLUE}📊 View logs: docker logs -f spoof53${NC}"
fi

echo ""
echo -e "${YELLOW}📝 Useful commands:${NC}"
echo -e "  ${GREEN}• Stop:${NC}    docker-compose down (or docker stop spoof53)"
echo -e "  ${GREEN}• Start:${NC}   docker-compose up -d (or docker start spoof53)"
echo -e "  ${GREEN}• Shell:${NC}   docker exec -it spoof53 bash"
echo -e "  ${GREEN}• Logs:${NC}    docker logs -f spoof53"
echo ""
echo -e "${GREEN}Access the interactive console with:${NC}"
echo -e "  ${BLUE}docker exec -it spoof53 python3 spoof53.py${NC}"