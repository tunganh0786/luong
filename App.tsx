import React, { useState, useEffect, useMemo } from 'react';
import DataTable from './components/DataTable';
import SummaryDashboard from './components/SummaryDashboard';
import SettingsModal from './components/SettingsModal';
import { DailyRecord, AppSettings, MonthlyConfig } from './types';
import { Settings, BrainCircuit, RefreshCcw, ChevronLeft, ChevronRight, Calendar, Download } from 'lucide-react';
import { analyzeFinances } from './services/geminiService';
import { exportToExcel } from './services/exportService';
import ReactMarkdown from 'react-markdown';

const STORAGE_KEY_RECORDS = 'finance_records_v1';
const STORAGE_KEY_SETTINGS = 'finance_settings_v1';
const STORAGE_KEY_MONTHLY_CONFIGS = 'finance_monthly_configs_v1';
const STORAGE_KEY_SELECTED_MONTH = 'finance_view_month_v1';

// Helper to get "YYYY-MM" string from date
const getMonthString = (date: Date) => {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
};

// Initial Data
const DEFAULT_SETTINGS: AppSettings = {
  exchangeRate: 5500,
  exchangeRateTH: 750,
  exchangeRateSG: 15600,

  baseSalary: 8000000,
  standardWorkDays: 24, // Mặc định 24 ngày
  supportSalary: 500000, // Mặc định 500k hỗ trợ support
  insuranceSupport: 1075000, // Mặc định 1.075k hỗ trợ BHXH

  unionFund: 50000,        // Quỹ công đoàn
  latePenaltyPerTime: 50000, // Phạt đi muộn

  percentOptimizationBonus: 25,

  // Specific Limits
  limitMY_BPO: 30,
  limitMY_BIO: 30,
  limitMY_UP: 35,

  limitTH_BPO: 35,
  limitTH_BIO: 35,
  limitTH_UP: 35,

  limitSG_BPO: 30,
  limitSG_BIO: 30,
  limitSG_UP: 35,
};

const DEFAULT_MONTHLY_CONFIG: MonthlyConfig = {
  // MY
  revenueBPO_MYR: 0,
  revenueBIO_MYR: 0,
  revenueMY_UP_MYR: 0,
  // TH
  revenueTH_BPO_THB: 0,
  revenueTH_BIO_THB: 0,
  revenueTH_UP_THB: 0,
  // SG
  revenueSG_BPO_SGD: 0,
  revenueSG_BIO_SGD: 0,
  revenueSG_UP_SGD: 0,

  actualWorkDays: 24, // Mặc định đủ công
  lateCount: 0,

  milestoneCounts: {},
};

const App: React.FC = () => {
  // State Initialization
  const [records, setRecords] = useState<DailyRecord[]>([]);
  const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);
  const [monthlyConfigs, setMonthlyConfigs] = useState<Record<string, MonthlyConfig>>({});

  // UI State
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'input' | 'summary'>('input');

  // Month Selection State - Initialize from storage or default to current
  const [selectedMonth, setSelectedMonth] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(STORAGE_KEY_SELECTED_MONTH);
      if (saved) return saved;
    }
    return getMonthString(new Date());
  });

  // AI State
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // --- Load Data from Local Storage (Once on Mount) ---
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const savedRecords = localStorage.getItem(STORAGE_KEY_RECORDS);
    const savedSettings = localStorage.getItem(STORAGE_KEY_SETTINGS);
    const savedMonthlyConfigs = localStorage.getItem(STORAGE_KEY_MONTHLY_CONFIGS);

    if (savedRecords) {
      try {
        setRecords(JSON.parse(savedRecords));
      } catch (e) {
        console.error("Failed to parse records", e);
      }
    }

    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings({
          ...DEFAULT_SETTINGS,
          ...parsedSettings,
        });
      } catch (e) {
        console.error("Failed to parse settings", e);
      }
    }

    if (savedMonthlyConfigs) {
      try {
        setMonthlyConfigs(JSON.parse(savedMonthlyConfigs));
      } catch (e) {
        console.error("Failed to parse monthly configs", e);
      }
    }

    setIsLoaded(true);
  }, []);

  // --- Save Data to Local Storage (On Change) ---
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY_RECORDS, JSON.stringify(records));
    }
  }, [records, isLoaded]);

  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY_SETTINGS, JSON.stringify(settings));
    }
  }, [settings, isLoaded]);

  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY_MONTHLY_CONFIGS, JSON.stringify(monthlyConfigs));
    }
  }, [monthlyConfigs, isLoaded]);

  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY_SELECTED_MONTH, selectedMonth);
    }
  }, [selectedMonth, isLoaded]);


  // --- Logic to Ensure Days Exist for Selected Month ---
  useEffect(() => {
    if (!selectedMonth) return;

    setRecords(prev => {
      const [year, month] = selectedMonth.split('-').map(Number);
      const daysInMonth = new Date(year, month, 0).getDate();

      const dateSet = new Set<string>();
      const uniqueRecords: DailyRecord[] = [];
      let hasChanges = false;

      // 1. Deduplicate existing records based on date
      for (const r of prev) {
        if (!dateSet.has(r.date)) {
          dateSet.add(r.date);
          uniqueRecords.push(r);
        } else {
          hasChanges = true;
        }
      }

      // 2. Add missing days for the selected month
      for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        if (!dateSet.has(dateStr)) {
          uniqueRecords.push({
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}-${day}`,
            date: dateStr,
            // MY
            costBPO: 0,
            costBIO: 0,
            costMY_UP: 0,
            // TH
            costTH_BPO: 0,
            costTH_BIO: 0,
            costTH_UP: 0,
            // SG
            costSG_BPO: 0,
            costSG_BIO: 0,
            costSG_UP: 0,
          });
          dateSet.add(dateStr);
          hasChanges = true;
        }
      }

      if (!hasChanges) return prev;

      // Return sorted records
      return uniqueRecords.sort((a, b) => a.date.localeCompare(b.date));
    });
  }, [selectedMonth, records.length]); // Check when month changes or records length changes (e.g. after load)

  // Derived filtered records for the selected month
  const filteredRecords = useMemo(() => {
    return records
      .filter(r => r.date.startsWith(selectedMonth))
      .sort((a, b) => a.date.localeCompare(b.date));
  }, [records, selectedMonth]);

  // Get current month config or default
  const currentMonthlyConfig = useMemo(() => {
    return monthlyConfigs[selectedMonth] || DEFAULT_MONTHLY_CONFIG;
  }, [monthlyConfigs, selectedMonth]);

  const handleMonthChange = (offset: number) => {
    const [year, month] = selectedMonth.split('-').map(Number);
    const currentDate = new Date(year, month - 1, 1);
    currentDate.setMonth(currentDate.getMonth() + offset);
    setSelectedMonth(getMonthString(currentDate));
    setAiAnalysis(null);
  };

  const handleSettingChange = (field: keyof AppSettings, value: number) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  const handleMonthlyConfigChange = (field: keyof MonthlyConfig, value: any) => {
    setMonthlyConfigs(prev => ({
      ...prev,
      [selectedMonth]: {
        ...(prev[selectedMonth] || DEFAULT_MONTHLY_CONFIG),
        [field]: value
      }
    }));
  };

  const formattedMonthDisplay = useMemo(() => {
    const [year, month] = selectedMonth.split('-').map(Number);
    return `Tháng ${String(month).padStart(2, '0')}/${year}`;
  }, [selectedMonth]);

  const handleAIAnalysis = async () => {
    setIsAnalyzing(true);
    setAiAnalysis(null);
    const result = await analyzeFinances(filteredRecords, settings, currentMonthlyConfig, formattedMonthDisplay);
    setAiAnalysis(result);
    setIsAnalyzing(false);
  };

  const handleExport = () => {
    exportToExcel(filteredRecords, settings, currentMonthlyConfig, formattedMonthDisplay);
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 py-3 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="w-8 h-8 bg-green-500 rounded flex items-center justify-center text-white font-bold shrink-0">
              A
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-800 leading-tight">Asia Finance Tracker</h1>
              <p className="text-xs text-gray-500 hidden md:block">Malaysia, Thailand & Singapore</p>
            </div>
          </div>

          <div className="flex items-center bg-gray-100 rounded-lg p-1 shadow-inner">
            <button
              onClick={() => handleMonthChange(-1)}
              className="p-1.5 hover:bg-white hover:shadow-sm rounded-md transition-all text-gray-600"
            >
              <ChevronLeft size={18} />
            </button>
            <div className="flex items-center gap-2 px-4 font-semibold text-gray-700 min-w-[140px] justify-center">
              <Calendar size={16} className="text-blue-500" />
              {formattedMonthDisplay}
            </div>
            <button
              onClick={() => handleMonthChange(1)}
              className="p-1.5 hover:bg-white hover:shadow-sm rounded-md transition-all text-gray-600"
            >
              <ChevronRight size={18} />
            </button>
          </div>

          <div className="flex items-center gap-2 absolute right-4 top-3 md:static md:top-auto md:right-auto">
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-green-700 bg-green-50 hover:bg-green-100 rounded-full transition-colors border border-green-200"
              title="Xuất file Excel"
            >
              <Download size={16} />
              <span className="hidden sm:inline">Xuất Excel</span>
            </button>

            <button
              onClick={() => setIsSettingsOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              title="Settings"
            >
              <Settings size={16} />
              <span className="hidden sm:inline">Cấu hình</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6 flex-1 flex flex-col">

        {/* Navigation Tabs (Mobile Only) */}
        <div className="lg:hidden flex space-x-1 bg-gray-200 p-1 rounded-lg w-full max-w-md mx-auto mb-2 md:mb-6 shrink-0">
          <button
            onClick={() => setActiveTab('input')}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${activeTab === 'input'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
              }`}
          >
            Nhập Chi Phí
          </button>
          <button
            onClick={() => setActiveTab('summary')}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${activeTab === 'summary'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
              }`}
          >
            Tổng Kết & Lương
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">

          {/* Left / Main Panel: Table */}
          <div className={`lg:col-span-7 flex flex-col h-full min-h-[500px] lg:min-h-0 ${activeTab === 'summary' ? 'hidden lg:flex' : 'flex'}`}>
            <DataTable
              records={filteredRecords}
              setRecords={setRecords}
              selectedMonth={selectedMonth}
            />
          </div>

          {/* Right / Bottom Panel: Summary Dashboard */}
          <div className={`lg:col-span-5 h-full overflow-y-auto space-y-6 pb-12 ${activeTab === 'input' ? 'hidden lg:block' : 'block'}`}>
            <SummaryDashboard
              records={filteredRecords}
              settings={settings}
              monthlyConfig={currentMonthlyConfig}
              onSettingChange={handleSettingChange}
              onMonthlyConfigChange={handleMonthlyConfigChange}
            />

            {/* AI Section */}
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-5 rounded-xl border border-indigo-100">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-indigo-800 font-bold flex items-center gap-2">
                  <BrainCircuit size={18} />
                  AI Phân Tích
                </h3>
                <button
                  onClick={handleAIAnalysis}
                  disabled={isAnalyzing}
                  className="text-xs bg-indigo-600 text-white px-3 py-1.5 rounded-full hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-1"
                >
                  {isAnalyzing ? <RefreshCcw className="animate-spin" size={12} /> : null}
                  {isAnalyzing ? 'Đang đọc...' : 'Phân tích'}
                </button>
              </div>

              {aiAnalysis ? (
                <div className="prose prose-sm prose-indigo max-w-none bg-white p-3 rounded-lg border border-indigo-50 shadow-sm max-h-60 overflow-y-auto">
                  <ReactMarkdown>{aiAnalysis}</ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm text-indigo-400 italic">
                  Nhập chi phí và doanh thu để AI phân tích hiệu quả.
                </p>
              )}
            </div>
          </div>

        </div>
      </main>

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        setSettings={setSettings}
      />
    </div>
  );
};

export default App;