
export interface DailyRecord {
  id: string;
  date: string;
  // Malaysia Market
  costBPO: number;      // VND (Legacy name for MY BPO)
  costBIO: number;      // VND (Legacy name for MY BIO)
  costMY_UP: number;    // VND (New: MY UP)

  // Thailand Market
  costTH_BPO: number;   // VND
  costTH_BIO: number;   // VND
  costTH_UP: number;    // VND (New: TH UP)

  // Singapore Market
  costSG_BPO: number;   // VND
  costSG_BIO: number;   // VND
  costSG_UP: number;    // VND
}

export interface MonthlyConfig {
  // Malaysia
  revenueBPO_MYR: number;
  revenueBIO_MYR: number;
  revenueMY_UP_MYR: number;

  // Thailand
  revenueTH_BPO_THB: number; 
  revenueTH_BIO_THB: number; 
  revenueTH_UP_THB: number;
  
  // Singapore
  revenueSG_BPO_SGD: number;
  revenueSG_BIO_SGD: number;
  revenueSG_UP_SGD: number;

  // Timekeeping
  actualWorkDays: number; // Số công thực tế
  lateCount: number;      // Số lần đi muộn

  milestoneCounts: Record<string, number>;
}

export interface AppSettings {
  // Global Settings
  exchangeRate: number;      // VND/MYR
  exchangeRateTH: number;    // VND/THB
  exchangeRateSG: number;    // VND/SGD
  
  // Salary Config
  baseSalary: number; // Lương cứng (Full)
  standardWorkDays: number; // Số ngày công chuẩn (VD: 24)
  supportSalary: number;
  insuranceSupport: number; // Hỗ trợ BHXH
  
  // Deductions
  unionFund: number;         // Quỹ công đoàn (VD: 50000)
  latePenaltyPerTime: number;// Phạt đi muộn mỗi lần (VD: 50000)
  
  // Cost Optimization Config (Specific Limits)
  percentOptimizationBonus: number; // Default 25% (Shared)
  
  // Malaysia Limits (%)
  limitMY_BPO: number;
  limitMY_BIO: number;
  limitMY_UP: number;

  // Thailand Limits (%)
  limitTH_BPO: number;
  limitTH_BIO: number;
  limitTH_UP: number;

  // Singapore Limits (%)
  limitSG_BPO: number;
  limitSG_BIO: number;
  limitSG_UP: number;
}

export interface AnalysisResult {
  markdown: string;
  loading: boolean;
}