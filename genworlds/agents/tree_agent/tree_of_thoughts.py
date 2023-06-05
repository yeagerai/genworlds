import time
from typing import Literal


class TreeOfThoughts:
    def __init__(self, 
            gen_thoughts: callable,
            eval_thoughts: callable, 
            search_algorithm: Literal["BFS", "DFS"],
            initial_state: str,
            thought_limit: int,
            max_depth: int,
            breadth: int,
            value_threshold: int,
            timeout: int = None,
        ):
        self.gen_thoughts = gen_thoughts
        self.eval_thoughts = eval_thoughts
        self.search_algorithm = search_algorithm
        self.initial_state = initial_state
        self.thought_limit = thought_limit
        self.max_depth = max_depth
        self.breadth = breadth
        self.value_threshold = value_threshold
        self.timeout = timeout

    def solve(
        self,
        llm_params: dict,
    ) -> list[str]:
        start_time = time.time()

        if self.search_algorithm == "BFS":
            return self.bfs_until_timeout(
                self.initial_state, 
                self.thought_limit, 
                self.max_depth, 
                self.breadth, 
                start_time, 
                self.timeout,
                llm_params,
            )
        elif self.search_algorithm == "DFS":
            return self.dfs_until_timeout(
                self.initial_state,
                self.thought_limit,
                self.max_depth,
                self.value_threshold,
                start_time,
                self.timeout,
                llm_params,
            )
        else:
            raise ValueError("Invalid search algorithm. Choose 'BFS' or 'DFS'.")

    def bfs_until_timeout(
        self, initial_state, thought_limit, max_depth, breadth, start_time, timeout, llm_params
    ):
        while timeout is None or time.time() - start_time < timeout:
            result = self.tot_bfs(initial_state, thought_limit, max_depth, breadth, llm_params)
            if result:
                return result

    def tot_bfs(self, initial_state, thought_limit, max_depth, breadth, llm_params):
        current_set = {initial_state}
        for _ in range(max_depth):
            current_set = self.expand_set(current_set, thought_limit, breadth, llm_params)
        print(current_set)
        print(max(current_set))
        # return self.gen_thoughts(max(current_set), 1, llm_params)
        return max(current_set)

    def expand_set(self, current_set, thought_limit, breadth, llm_params):
        new_set = {
            (*state, new_thought)
            for state in current_set
            for new_thought in self.gen_thoughts(state, thought_limit, llm_params)
        }
        if (thought_limit == 1):
            return new_set
        else:
            thought_values = self.eval_thoughts(new_set, llm_params)
            sorted_set = sorted(
                new_set, key=lambda state: thought_values[state], reverse=True
            )
            return set(sorted_set[:breadth])

    def dfs_until_timeout(
        self,
        initial_state,
        thought_limit,
        max_depth,
        value_threshold,
        start_time,
        timeout,
        llm_params,
    ):
        while timeout is None or time.time() - start_time < timeout:
            result = self.tot_dfs(
                initial_state, thought_limit, max_depth, value_threshold, llm_params
            )
            if result:
                return result

    def tot_dfs(
        self,
        initial_state,
        thought_limit,
        max_depth,
        value_threshold,
        llm_params,
        pruning_threshold=0.5,
        confidence_threshold=0.9,
        max_iterations=10,
        convergence_threshold=0.1,
        convergence_count=5,
    ):
        output, iteration_count, consecutive_convergence_count, prev_best_value = (
            [],
            0,
            0,
            None,
        )
        self.dfs_search(
            initial_state,
            1,
            max_depth,
            thought_limit,
            value_threshold,
            pruning_threshold,
            confidence_threshold,
            output,
            iteration_count,
            consecutive_convergence_count,
            prev_best_value,
            max_iterations,
            convergence_threshold,
            convergence_count,
            llm_params,
        )
        return max(output, key=lambda output_item: output_item[1]) if output else None

    def dfs_search(
        self,
        current_state,
        current_depth,
        max_depth,
        thought_limit,
        value_threshold,
        pruning_threshold,
        confidence_threshold,
        output,
        iteration_count,
        consecutive_convergence_count,
        prev_best_value,
        max_iterations,
        convergence_threshold,
        convergence_count,
        llm_params,
    ):
        if current_depth > max_depth or self.should_terminate(
            output,
            iteration_count,
            consecutive_convergence_count,
            max_iterations,
            convergence_count,
            confidence_threshold,
            convergence_threshold,
            prev_best_value,
        ):
            return
        for next_state in self.gen_thoughts(current_state, thought_limit, llm_params):
            state_value = self.eval_thoughts({next_state}, llm_params)[next_state]
            if state_value > value_threshold and (
                pruning_threshold is None or state_value >= pruning_threshold
            ):
                self.dfs_search(
                    (*current_state, next_state),
                    current_depth + 1,
                    max_depth,
                    thought_limit,
                    value_threshold,
                    pruning_threshold,
                    confidence_threshold,
                    output,
                    iteration_count,
                    consecutive_convergence_count,
                    prev_best_value,
                    max_iterations,
                    convergence_threshold,
                    convergence_count,
                    llm_params,
                )

    def should_terminate(
        self,
        output,
        iteration_count,
        consecutive_convergence_count,
        max_iterations,
        convergence_count,
        confidence_threshold,
        convergence_threshold,
        prev_best_value,
    ):
        if (
            iteration_count >= max_iterations
            or consecutive_convergence_count >= convergence_count
        ):
            return True
        if output:
            thought, value = output[-1]
            if value >= confidence_threshold or (
                prev_best_value is not None
                and abs(value - prev_best_value) < convergence_threshold
            ):
                return True
        return False
