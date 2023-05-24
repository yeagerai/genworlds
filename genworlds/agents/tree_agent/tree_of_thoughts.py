import time


class TreeOfThoughts:
    def __init__(self, thought_model, search_algorithm):
        self.thought_model = thought_model
        self.search_algorithm = search_algorithm

    def solve(
        self,
        initial_state,
        thought_limit,
        max_depth,
        breadth,
        value_threshold,
        timeout=None,
    ):
        start_time = time.time()

        if self.search_algorithm == "BFS":
            return self.bfs_until_timeout(
                initial_state, thought_limit, max_depth, breadth, start_time, timeout
            )
        elif self.search_algorithm == "DFS":
            return self.dfs_until_timeout(
                initial_state,
                thought_limit,
                max_depth,
                value_threshold,
                start_time,
                timeout,
            )
        else:
            raise ValueError("Invalid search algorithm. Choose 'BFS' or 'DFS'.")

    def bfs_until_timeout(
        self, initial_state, thought_limit, max_depth, breadth, start_time, timeout
    ):
        while timeout is None or time.time() - start_time < timeout:
            result = self.tot_bfs(initial_state, thought_limit, max_depth, breadth)
            if result:
                return result

    def tot_bfs(self, initial_state, thought_limit, max_depth, breadth):
        current_set = {initial_state}
        for _ in range(max_depth):
            current_set = self.expand_set(current_set, thought_limit, breadth)
        return self.thought_model.gen_thoughts(max(current_set), 1)

    def expand_set(self, current_set, thought_limit, breadth):
        new_set = {
            (*state, new_thought)
            for state in current_set
            for new_thought in self.thought_model.gen_thoughts(state, thought_limit)
        }
        thought_values = self.thought_model.eval_thoughts(new_set)
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
    ):
        while timeout is None or time.time() - start_time < timeout:
            result = self.tot_dfs(
                initial_state, thought_limit, max_depth, value_threshold
            )
            if result:
                return result

    def tot_dfs(
        self,
        initial_state,
        thought_limit,
        max_depth,
        value_threshold,
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
        for next_state in self.thought_model.gen_thoughts(current_state, thought_limit):
            state_value = self.thought_model.eval_thoughts({next_state})[next_state]
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
