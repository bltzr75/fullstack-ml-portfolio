import { IsString, IsOptional, IsEnum, IsDateString } from 'class-validator';

export class CreateTodoDto {
  @IsString()
  title: string;

  @IsOptional()
  @IsString()
  description?: string;

  @IsEnum(['low', 'medium', 'high'])
  priority: 'low' | 'medium' | 'high';

  @IsOptional()
  @IsDateString()
  dueDate?: string;
}
