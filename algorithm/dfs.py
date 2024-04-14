def dfs(graph, start_node):
    # 방문한 노드를 저장할 집합
    visited = set()
    # 스택에 시작 노드 추가
    stack = [start_node]

    while stack:
        # 스택에서 하나의 원소를 꺼냄
        node = stack.pop()
        if node not in visited:
            # 현재 노드를 방문 처리
            print(node, end=" ")
            visited.add(node)
            # 인접 노드 중 방문하지 않은 노드를 스택에 추가
            for neighbor in reversed(
                graph[node]
            ):  # 노드를 방문 순서대로 처리하기 위해 역순으로 추가
                if neighbor not in visited:
                    stack.append(neighbor)


graph = {1: {2, 3}, 2: {1, 4, 5}, 3: {1, 6}, 4: {2}, 5: {2}, 6: {3}}

bfs_result = dfs(graph, 1)
print("BFS 탐색 순서:", bfs_result)
