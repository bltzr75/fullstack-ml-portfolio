import { Todo } from '../types/todo';
import { FilterType, SortType } from '../store/todoSlice';

export const filterTodos = (todos: Todo[], filter: FilterType): Todo[] => {
  switch (filter) {
    case 'active':
      return todos.filter(todo => !todo.completed);
    case 'completed':
      return todos.filter(todo => todo.completed);
    default:
      return todos;
  }
};

export const sortTodos = (todos: Todo[], sort: SortType): Todo[] => {
  const sortedTodos = [...todos];
  
  switch (sort) {
    case 'priority':
      return sortedTodos.sort((a, b) => {
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      });
    
    case 'dueDate':
      return sortedTodos.sort((a, b) => {
        // Todos without due dates go to the end
        if (!a.dueDate && !b.dueDate) return 0;
        if (!a.dueDate) return 1;
        if (!b.dueDate) return -1;
        return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
      });
    
    case 'created':
    default:
      return sortedTodos.sort((a, b) => 
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      );
  }
};

export const getFilteredAndSortedTodos = (
  todos: Todo[], 
  filter: FilterType, 
  sort: SortType
): Todo[] => {
  const filtered = filterTodos(todos, filter);
  return sortTodos(filtered, sort);
};
