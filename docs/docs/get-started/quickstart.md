---
sidebar_position: 2
---

# Quickstart

Whether you're a creator dreaming up new simulated worlds, or a developer looking to enhance the GenWorlds framework and tools, our quickstart guides have got you covered.

:::tip Info

GenWorlds utilizes GPT-4, which is currently accessible to those who have made at least one successful payment through https://platform.openai.com/.

:::

## For Creators: Building Your Own Simulated Worlds

### Running with Replit

The easiest way to start using GenWorlds Community Edition is through Replit. Click [here](https://replit.com/@yeagerai/GenWorlds) to fork it and run it on Replit.

### Running with Docker

To set up and run GenWorlds Community Edition with Docker, use the following commands:

```sh
git clone git@github.com:yeagerai/genworlds-community.git
```

Then create a file called `.env` and copy the content of the `.env.example` and replace the corresponding API keys.

After that, to build and run the image:

```sh
docker build -t genworlds-world-app -f ./deployments/docker/Dockerfile .
docker run -p 80:80 -p 9000:9000 -d genworlds-world-app
```

Finally, you can open your browser and go to `http://localhost/home`. If you want to go directly to a use-case, you can go to `http://localhost/use-case/roundtable/agents_of_change.yaml`.

If you want the app to directly launch a specific use-case, you can add the following variable to the `.env` file:

```bash
VUE_APP_USE_CASE_ACCESS_POINT=/use_cases/roundtable/presidential_debate.yaml
```

If you want to start from the gallery and see all the use-cases, delete the environment variable `VUE_APP_USE_CASE_ACCESS_POINT` from `.env`.

After that you can modify the `.yaml` files to start creating new roundtables.

For more information about the community toolkit, check [this](/docs/category/community-toolkit) out.

## For Developers: Enhancing the Framework and Tools

You can find a detailed guide [here](/docs/genworlds-framework/devs-guide/).
