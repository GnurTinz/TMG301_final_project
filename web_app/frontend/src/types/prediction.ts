export type Category = 'Payment' | 'Return/Refund' | 'Technical Issue';
export type Priority = 'Urgent' | 'High' | 'Medium' | 'Needs Human Review';

export interface RoutingDecision {
  category: Category;
  category_vi: string;
  target_department: string;
  dept_code: string;
  confidence_score: number;
  all_class_probabilities: Record<Category, number>;
  priority_level: Priority;
  sla_hours: number;
}

export interface TicketResult {
  ticket_id: string;
  timestamp: string;
  customer_email: string;
  customer_message: string;
  routing_decision: RoutingDecision;
  automated_response: string;
}

export interface TicketInput {
  message: string;
  customer_email: string;
}

export interface Sample {
  id: string;
  sender: string;
  subject: string;
  text: string;
  tag: string;
}

export interface Health {
  success: boolean;
  status: 'ready' | 'unavailable';
  model_ready: boolean;
  model_name: string | null;
}

export interface ModelInfo {
  success: boolean;
  model_name: string;
  classes: Category[];
  metrics: { accuracy: number; macro_f1: number; test_samples: number; train_samples: number };
  label_mappings: Record<Category, { vi_name: string; department: string; dept_code: string; default_priority: string; sla_hours: number }>;
}

export interface ClassMetrics {
  precision: number;
  recall: number;
  'f1-score': number;
  support: number;
}

export interface ModelMetrics {
  accuracy: number;
  balanced_accuracy: number;
  macro_precision: number;
  macro_recall: number;
  macro_f1: number;
  weighted_f1: number;
  train_time_sec: number;
  infer_time_sec: number;
  classification_report: Record<Category, ClassMetrics>;
  confusion_matrix: number[][];
}

export interface Plot {
  id: string;
  title: string;
  filename: string;
  description: string;
}

export interface DashboardData {
  success: boolean;
  models_summary: Record<string, ModelMetrics>;
  plots: Plot[];
  dataset_stats: {
    total_samples: number;
    train_samples: number;
    val_samples: number;
    test_samples: number;
    classes: Record<Category, { count: number; percentage: number; vi_name: string; dept: string }>;
  };
}
