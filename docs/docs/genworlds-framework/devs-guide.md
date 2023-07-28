---
sidebar_position: 5
---

# Developer Guide

Welcome to the Genworlds development guide. This document will guide you through setting up your development environment and give you a quick introduction to the best practices for developing the Genworlds framework.

## Development Setup

To get started with Genworlds, follow the steps outlined below:

### Step 1: Cloning the Repositories

Clone the `genworlds` and `genworlds-community` repositories. Both repositories need to be cloned into the same parent directory.

```bash
git clone git@github.com:yeagerai/genworlds.git
git clone git@github.com:yeagerai/genworlds-community.git
```

### Step 2: Install JS Dependencies

Navigate to the `genworlds-community/packages/16bit-back` directory and execute this:

```bash
nvm use
npm ci
```

Navigate to the `genworlds-community/packages/16bit-front` directory and execute this:

```bash
yarn setup
```

Navigate to the `genworlds-community/packages/nano-vue` directory and execute this:

```bash
yarn install
```

Navigate to the `genworlds-community/packages/gateway` directory and execute this:

```bash
npm install
```

### Step 3: Docker Compose

Navigate to the `genworlds-community` directory and start the Docker Compose:

```bash
docker-compose up
```

### Step 3: Set API keys

After the Docker containers are up and running, you need to set your `OPENAI_API_KEY` in the `.env` file:

```bash
echo "OPENAI_API_KEY=your-openai-api-key" >> .env
```

Again, ensure that your-openai-api-key is replaced with your actual OpenAI API key.

## Developing Genworlds

Once your development environment is set up, you can begin modifying the Genworlds framework. Any changes made to the framework can be seen by restarting the `world-instance` container.

Typically, development work involves modifying the use-case slightly. You can find the use-cases in the `genworlds-community/use_cases/roundtable/world_definitions` directory. They are defined in the YAML files located in this directory.

:::tip Info

Sometimes the 16bit-back server gets a connection refused error while trying to connect to the socket. If this happens, you can restart the `16bit-back` container to fix the issue.

:::

## Conclusion

Thank you for choosing to contribute to the Genworlds project! We appreciate your efforts in improving and expanding the functionality of our framework. If you need help or have any questions, please don't hesitate to ask. Happy coding!
