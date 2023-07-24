---
sidebar_position: 2
---

# Quickstart

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

After that you can modify the `.yaml` files to start creating new roundtables.

For more information about the community toolkit, check [this](/docs/category/community-toolkit) out.

## For Developers: Enhancing the Framework and Tools

1. Set Up Your Development Environment
Clone the GenWorlds repository and set up a development environment.

    git clone git@github.com:yeagerai/genworlds.git
    cd genworlds
    pip install -e .

2. Understand the Code Structure
Spend time understanding the architecture and codebase of GenWorlds. Familiarize yourself with the structure and the functionality of the different parts of the code. You can find more information [here](/docs/category/the-genworlds-framework).

3. Make Improvements
Whether it's adding new features, fixing bugs, or improving documentation, contribute your enhancements back to the project.

    git checkout -b my-feature
    git commit -am "Add my new feature"
    git push origin my-feature

4. Submit a Pull Request
Once you're satisfied with your changes, submit a pull request for review.

Remember to follow the guidelines for contributing, which can be found in [CONTRIBUTING.md](https://github.com/yeagerai/genworlds/blob/main/CONTRIBUTING.md) in the project repository.
