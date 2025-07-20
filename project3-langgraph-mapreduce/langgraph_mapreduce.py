#!/usr/bin/env python3
"""
LangGraph Map-Reduce implementation for sum of squares calculation.
Uses Send API for parallel execution of mapper nodes.
Based on the Medium tutorial pattern.
"""

import operator
import random
import time
from typing import Annotated, List, Dict, Any, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send


# Define the overall state that flows through the main graph
class OverallState(TypedDict):
    """Main state passed through the graph."""
    length: int
    numbers: List[int]
    squared_results: Annotated[List[int], operator.add]  # Aggregates results from mappers
    sum_of_squares: int
    execution_time: float


# Define the mapper state for individual number processing
class MapperState(TypedDict):
    """State for individual mapper nodes."""
    number: int


def generator_node(state: OverallState) -> Dict[str, Any]:
    """
    Generator Node: Create a list of random integers (0-99).
    This is the Map phase setup.
    """
    print(f"🎲 Generator: Creating {state['length']} random numbers...")
    start_time = time.time()
    
    # Generate random numbers
    numbers = [random.randint(0, 99) for _ in range(state['length'])]
    
    end_time = time.time()
    print(f"✅ Generator: Created numbers: {numbers[:5]}{'...' if len(numbers) > 5 else ''}")
    print(f"⏱️  Generator execution time: {end_time - start_time:.4f}s")
    
    return {
        "numbers": numbers,
        "execution_time": end_time - start_time
    }


def mapper_node(state: MapperState) -> Dict[str, Any]:
    """
    Mapper Node: Square a single number.
    Each mapper processes one number in parallel.
    This is the Map phase execution.
    """
    number = state["number"]
    squared = number ** 2
    
    print(f"🔢 Mapper: {number}² = {squared}")
    
    # Return in the format expected by the aggregated state
    return {"squared_results": [squared]}


def reducer_node(state: OverallState) -> Dict[str, Any]:
    """
    Reducer Node: Sum all squared results.
    This is the Reduce phase.
    """
    print("🔄 Reducer: Summing all squared results...")
    start_time = time.time()
    
    # Sum all the squared results that were aggregated
    total_sum = sum(state['squared_results'])
    
    end_time = time.time()
    print(f"✅ Reducer: Sum of squares = {total_sum}")
    print(f"📊 Processed {len(state['squared_results'])} numbers")
    print(f"⏱️  Reducer execution time: {end_time - start_time:.4f}s")
    
    return {
        "sum_of_squares": total_sum,
        "execution_time": state['execution_time'] + (end_time - start_time)
    }


def continue_to_mappers(state: OverallState) -> List[Send]:
    """
    Create Send objects for parallel mapper execution.
    This implements the fan-out pattern using LangGraph's Send API.
    """
    print(f"📤 Creating {len(state['numbers'])} parallel mapper tasks...")
    
    # Create a Send object for each number to be processed in parallel
    sends = [Send("mapper", {"number": num}) for num in state['numbers']]
    
    print(f"✅ Created {len(sends)} Send objects for parallel processing")
    return sends


def create_mapreduce_graph() -> StateGraph:
    """
    Create the LangGraph StateGraph with map-reduce pattern.
    Uses the Send API for parallel execution.
    """
    print("🏗️  Building LangGraph Map-Reduce graph...")
    
    # Create the graph with the overall state
    graph = StateGraph(OverallState)
    
    # Add nodes
    graph.add_node("generator", generator_node)
    graph.add_node("mapper", mapper_node)
    graph.add_node("reducer", reducer_node)
    
    # Add edges
    graph.add_edge(START, "generator")
    
    # Fan-out: Generator creates Send objects for parallel mappers
    # This is the key pattern from the Medium post
    graph.add_conditional_edges(
        "generator",
        continue_to_mappers,
        ["mapper"]
    )
    
    # Fan-in: All mappers automatically aggregate to reducer
    graph.add_edge("mapper", "reducer")
    graph.add_edge("reducer", END)
    
    print("✅ Graph structure created with Send API pattern")
    return graph


def run_mapreduce(length: int) -> Dict[str, Any]:
    """
    Execute the map-reduce graph with the given length.
    
    Args:
        length: Number of random integers to generate and process
        
    Returns:
        Dictionary with sum_of_squares and execution metadata
    """
    print(f"\n🚀 Starting Map-Reduce execution for length={length}")
    print("=" * 60)
    
    # Create and compile the graph
    graph = create_mapreduce_graph()
    compiled_graph = graph.compile()
    
    # Initial state
    initial_state = {
        "length": length,
        "numbers": [],
        "squared_results": [],  # Will be aggregated by operator.add
        "sum_of_squares": 0,
        "execution_time": 0.0
    }
    
    # Execute the graph
    overall_start_time = time.time()
    
    try:
        # Run the compiled graph
        result = compiled_graph.invoke(initial_state)
        
        overall_end_time = time.time()
        total_time = overall_end_time - overall_start_time
        
        print("\n" + "=" * 60)
        print(f"🎉 Map-Reduce completed successfully!")
        print(f"📊 Results:")
        print(f"   - Input length: {length}")
        print(f"   - Numbers generated: {len(result['numbers'])}")
        print(f"   - Mappers executed: {len(result['squared_results'])}")
        print(f"   - Sum of squares: {result['sum_of_squares']}")
        print(f"   - Total execution time: {total_time:.4f}s")
        
        return {
            "sum_of_squares": result["sum_of_squares"],
            "length": length,
            "execution_time": total_time,
            "numbers_processed": len(result["squared_results"]),
            "sample_numbers": result["numbers"][:10]  # First 10 for reference
        }
        
    except Exception as e:
        print(f"❌ Error during graph execution: {e}")
        raise


# LangGraph Studio Integration Functions
def get_compiled_graph():
    """
    Return a compiled graph for LangGraph Studio.
    This is the entry point that LangGraph Studio will use.
    """
    graph = create_mapreduce_graph()
    compiled_graph = graph.compile()
    return compiled_graph


def create_graph():
    """
    Alternative entry point for LangGraph Studio.
    Returns the uncompiled graph.
    """
    return create_mapreduce_graph()


# Entry point for LangGraph Studio
# This is what LangGraph Studio will look for
app = get_compiled_graph()

# Alternative alias that some LangGraph tools expect
graph = create_mapreduce_graph()


if __name__ == "__main__":
    # Test the map-reduce implementation
    test_lengths = [3, 5, 10]
    
    for length in test_lengths:
        try:
            result = run_mapreduce(length)
            print(f"\n✅ Test passed for length {length}: sum = {result['sum_of_squares']}")
        except Exception as e:
            print(f"\n❌ Test failed for length {length}: {e}")
