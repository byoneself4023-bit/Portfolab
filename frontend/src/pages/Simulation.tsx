import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { portfolioAPI, stockAPI, simulationAPI, aiAPI } from '../api';

interface Stock {
  stock_no: number;
  symbol: string;
  name: string;
  current_price: number;
}

interface PortfolioStock {
  stock_no: number;
  symbol: string;
  name: string;
  quantity: number;
  avg_price: number;
  current_price: number;
}

interface SimulationChange {
  stock_no?: number;
  symbol?: string;
  quantity_delta?: number;
  quantity?: number;
  price?: number;
  name?: string;
}

interface AIAnalysis {
  risk_analysis: string;
  recommendation: string;
  overall_comment: string;
}

interface RebalanceSuggestion {
  current_status: string;
  suggestions: Array<{
    stock: string;
    action: string;
    quantity: string;
    reason: string;
  }>;
  expected_result: string;
}

// 지표 해석 함수들
const getVolatilityInfo = (vol: number) => {
  if (vol < 15) return { level: '매우 낮음', color: 'text-blue-400', desc: '국채/예금 수준의 안정적인 포트폴리오입니다.' };
  if (vol < 25) return { level: '낮음', color: 'text-emerald-400', desc: '대형 우량주 수준으로 안정적입니다.' };
  if (vol < 35) return { level: '보통', color: 'text-yellow-400', desc: '일반적인 주식 포트폴리오 수준입니다.' };
  if (vol < 50) return { level: '높음', color: 'text-orange-400', desc: '변동성이 높아 주의가 필요합니다.' };
  return { level: '매우 높음', color: 'text-red-400', desc: '고위험 포트폴리오입니다. 분산투자를 권장합니다.' };
};

const getSharpeInfo = (sharpe: number) => {
  if (sharpe < 0) return { level: '나쁨', color: 'text-red-400', desc: '무위험 수익률보다 낮습니다. 포트폴리오 재검토가 필요합니다.' };
  if (sharpe < 0.5) return { level: '부족', color: 'text-orange-400', desc: '위험 대비 수익이 낮습니다. 개선이 필요합니다.' };
  if (sharpe < 1.0) return { level: '양호', color: 'text-yellow-400', desc: '적정 수준입니다. 조금 더 개선 가능합니다.' };
  if (sharpe < 2.0) return { level: '우수', color: 'text-emerald-400', desc: '좋은 투자입니다. 위험 대비 수익이 우수합니다.' };
  return { level: '매우 우수', color: 'text-blue-400', desc: '뛰어난 투자입니다. 현재 전략을 유지하세요.' };
};

export default function Simulation() {
  const { id } = useParams();
  const portfolioNo = Number(id);

  const [portfolioStocks, setPortfolioStocks] = useState<PortfolioStock[]>([]);
  const [allStocks, setAllStocks] = useState<Stock[]>([]);
  const [changes, setChanges] = useState<SimulationChange[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);

  const [showAddNew, setShowAddNew] = useState(false);
  const [newStockNo, setNewStockNo] = useState<number | null>(null);
  const [newQuantity, setNewQuantity] = useState('');
  const [newPrice, setNewPrice] = useState('');

  // AI 분석 상태
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [showAiPanel, setShowAiPanel] = useState(false);

  // 리밸런싱 상태
  const [rebalanceSuggestion, setRebalanceSuggestion] = useState<RebalanceSuggestion | null>(null);
  const [rebalanceLoading, setRebalanceLoading] = useState(false);
  const [showRebalancePanel, setShowRebalancePanel] = useState(false);
  const [targetVolatility, setTargetVolatility] = useState('30');

  // 활성 탭 (ai | rebalance)
  const [activeTab, setActiveTab] = useState<'ai' | 'rebalance'>('ai');

  useEffect(() => {
    loadData();
  }, [portfolioNo]);

  const loadData = async () => {
    try {
      const [stocksRes, allStocksRes] = await Promise.all([
        portfolioAPI.getStocks(portfolioNo),
        stockAPI.getList()
      ]);
      setPortfolioStocks(stocksRes.data.data?.stocks || []);
      setAllStocks(allStocksRes.data.data || []);
    } catch (error) {
      console.error('데이터 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuantityChange = (stockNo: number, delta: number, stockName: string) => {
    setChanges(prev => {
      const existing = prev.find(c => c.stock_no === stockNo);
      if (existing) {
        const newDelta = (existing.quantity_delta || 0) + delta;
        if (newDelta === 0) {
          return prev.filter(c => c.stock_no !== stockNo);
        }
        return prev.map(c => 
          c.stock_no === stockNo ? { ...c, quantity_delta: newDelta } : c
        );
      }
      return [...prev, { stock_no: stockNo, quantity_delta: delta, name: stockName }];
    });
  };

  const handleAddNewStock = () => {
    if (!newStockNo || !newQuantity) {
      alert('종목과 수량을 입력해주세요.');
      return;
    }
    const stock = allStocks.find(s => s.stock_no === newStockNo);
    if (!stock) return;

    setChanges(prev => [
      ...prev,
      {
        symbol: stock.symbol,
        quantity: Number(newQuantity),
        price: Number(newPrice) || stock.current_price,
        name: stock.name
      }
    ]);
    setShowAddNew(false);
    setNewStockNo(null);
    setNewQuantity('');
    setNewPrice('');
  };

  const removeChange = (index: number) => {
    setChanges(prev => prev.filter((_, i) => i !== index));
  };

  const runSimulation = async () => {
    if (changes.length === 0) {
      alert('변경사항을 추가해주세요.');
      return;
    }
    setSimulating(true);
    try {
      const response = await simulationAPI.preview(portfolioNo, changes);
      if (response.data.success) {
        setResult(response.data.data);
      } else {
        alert(response.data.message || '시뮬레이션 실패');
      }
    } catch (error: any) {
      alert(error.response?.data?.message || '시뮬레이션에 실패했습니다.');
    } finally {
      setSimulating(false);
    }
  };

  // AI 분석 실행
  const runAiAnalysis = async () => {
    setAiLoading(true);
    setShowAiPanel(true);
    setActiveTab('ai');
    try {
      const response = await aiAPI.analyze(portfolioNo);
      if (response.data.success) {
        setAiAnalysis(response.data.data);
      } else {
        alert(response.data.message || 'AI 분석 실패');
      }
    } catch (error: any) {
      alert(error.response?.data?.message || 'AI 분석에 실패했습니다.');
    } finally {
      setAiLoading(false);
    }
  };

  // 리밸런싱 제안 실행
  const runRebalance = async () => {
    setRebalanceLoading(true);
    setShowRebalancePanel(true);
    setActiveTab('rebalance');
    try {
      const response = await aiAPI.rebalance(portfolioNo, Number(targetVolatility));
      if (response.data.success) {
        setRebalanceSuggestion(response.data.data);
      } else {
        alert(response.data.message || '리밸런싱 분석 실패');
      }
    } catch (error: any) {
      alert(error.response?.data?.message || '리밸런싱 분석에 실패했습니다.');
    } finally {
      setRebalanceLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-2 border-white/20 border-t-purple-400 rounded-full animate-spin"></div>
          <p className="text-white/50 text-sm tracking-widest uppercase">Loading</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-1/4 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-1/4 -right-1/4 w-[600px] h-[600px] bg-pink-500/10 rounded-full blur-[120px]"></div>
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50">
        <div className="absolute inset-0 bg-[#0a0a0f]/60 backdrop-blur-2xl border-b border-white/5"></div>
        <div className="relative max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl blur-lg opacity-50"></div>
              <div className="relative w-11 h-11 bg-gradient-to-br from-purple-400 to-pink-600 rounded-xl flex items-center justify-center">
                <span className="text-xl font-black">P</span>
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">PortfoLab</h1>
              <p className="text-[10px] text-white/40 tracking-[0.2em] uppercase">Simulation</p>
            </div>
          </Link>
          <div className="flex items-center gap-3">
            <button
              onClick={runAiAnalysis}
              disabled={aiLoading}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-lg hover:from-cyan-500/30 hover:to-blue-500/30 transition-all text-sm text-cyan-400"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              {aiLoading ? 'AI 분석 중...' : 'AI 분석'}
            </button>
            <Link to={`/portfolio/${portfolioNo}`} className="text-white/40 hover:text-white text-sm transition-all hover:bg-white/5 px-4 py-2 rounded-lg">
              ← 포트폴리오로
            </Link>
          </div>
        </div>
      </header>

      <main className="relative max-w-7xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">포트폴리오 시뮬레이터</h1>
          <p className="text-white/40">종목을 추가하거나 수량을 변경하면 예상 수익과 리스크를 미리 확인할 수 있어요</p>
        </div>

        {/* AI 분석 & 리밸런싱 패널 */}
        {(showAiPanel || showRebalancePanel) && (
          <div className="mb-6 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 rounded-2xl p-6">
            {/* 탭 헤더 */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setActiveTab('ai')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    activeTab === 'ai'
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'text-white/40 hover:text-white/60'
                  }`}
                >
                  AI 분석
                </button>
                <button
                  onClick={() => setActiveTab('rebalance')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    activeTab === 'rebalance'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'text-white/40 hover:text-white/60'
                  }`}
                >
                  최적 비중 제안
                </button>
              </div>
              <button
                onClick={() => {
                  setShowAiPanel(false);
                  setShowRebalancePanel(false);
                }}
                className="text-white/30 hover:text-white transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* AI 분석 탭 */}
            {activeTab === 'ai' && (
              <>
                {aiLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="flex flex-col items-center gap-4">
                      <div className="w-12 h-12 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin"></div>
                      <p className="text-white/50 text-sm">AI가 포트폴리오를 분석하고 있어요...</p>
                    </div>
                  </div>
                ) : aiAnalysis ? (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-6 h-6 bg-orange-500/20 rounded-lg flex items-center justify-center">
                          <svg className="w-3 h-3 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                        </div>
                        <h3 className="text-sm font-medium text-orange-400">리스크 분석</h3>
                      </div>
                      <p className="text-white/70 text-sm leading-relaxed">{aiAnalysis.risk_analysis}</p>
                    </div>
                    <div className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-6 h-6 bg-emerald-500/20 rounded-lg flex items-center justify-center">
                          <svg className="w-3 h-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <h3 className="text-sm font-medium text-emerald-400">투자 제안</h3>
                      </div>
                      <p className="text-white/70 text-sm leading-relaxed">{aiAnalysis.recommendation}</p>
                    </div>
                    <div className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-6 h-6 bg-purple-500/20 rounded-lg flex items-center justify-center">
                          <svg className="w-3 h-3 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                        </div>
                        <h3 className="text-sm font-medium text-purple-400">종합 평가</h3>
                      </div>
                      <p className="text-white/70 text-sm leading-relaxed">{aiAnalysis.overall_comment}</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-white/40">AI 분석 버튼을 클릭하세요</p>
                  </div>
                )}
              </>
            )}

            {/* 리밸런싱 탭 */}
            {activeTab === 'rebalance' && (
              <>
                {/* 목표 변동성 입력 */}
                <div className="flex items-center gap-4 mb-6">
                  <div className="flex items-center gap-2">
                    <span className="text-white/60 text-sm">목표 변동성:</span>
                    <input
                      type="number"
                      value={targetVolatility}
                      onChange={(e) => setTargetVolatility(e.target.value)}
                      className="w-20 px-3 py-2 bg-white/[0.03] border border-white/10 rounded-lg text-white text-center focus:outline-none focus:border-emerald-500/50"
                    />
                    <span className="text-white/40 text-sm">%</span>
                  </div>
                  <button
                    onClick={runRebalance}
                    disabled={rebalanceLoading}
                    className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg text-sm font-medium hover:from-emerald-400 hover:to-teal-400 transition-all disabled:opacity-50"
                  >
                    {rebalanceLoading ? '분석 중...' : '최적 비중 계산'}
                  </button>
                </div>

                {rebalanceLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="flex flex-col items-center gap-4">
                      <div className="w-12 h-12 border-2 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin"></div>
                      <p className="text-white/50 text-sm">최적 비중을 계산하고 있어요...</p>
                    </div>
                  </div>
                ) : rebalanceSuggestion ? (
                  <div className="space-y-4">
                    {/* 현재 상태 */}
                    <div className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                      <h4 className="text-sm font-medium text-white/60 mb-2">현재 상태</h4>
                      <p className="text-white/80 text-sm">{rebalanceSuggestion.current_status}</p>
                    </div>

                    {/* 제안 목록 */}
                    <div className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                      <h4 className="text-sm font-medium text-emerald-400 mb-3">리밸런싱 제안</h4>
                      <div className="space-y-3">
                        {rebalanceSuggestion.suggestions.map((s, i) => (
                          <div key={i} className="flex items-center justify-between bg-white/[0.02] p-3 rounded-lg">
                            <div className="flex items-center gap-3">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                s.action === '매수' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                              }`}>
                                {s.action}
                              </span>
                              <span className="text-white font-medium">{s.stock}</span>
                              <span className="text-white/60 text-sm">{s.quantity}</span>
                            </div>
                            <span className="text-white/40 text-xs max-w-[200px] text-right">{s.reason}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* 예상 결과 */}
                    <div className="bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 rounded-xl p-4">
                      <h4 className="text-sm font-medium text-emerald-400 mb-2">예상 결과</h4>
                      <p className="text-white/80 text-sm">{rebalanceSuggestion.expected_result}</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-white/40">목표 변동성을 입력하고 계산 버튼을 클릭하세요</p>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Holdings & Changes */}
          <div className="space-y-6">
            {/* Current Holdings */}
            <div className="bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <h2 className="text-lg font-semibold mb-4">현재 보유 종목</h2>
              {portfolioStocks.length === 0 ? (
                <p className="text-white/40 text-center py-8">보유 종목이 없습니다.</p>
              ) : (
                <div className="space-y-3">
                  {portfolioStocks.map(stock => (
                    <div key={stock.stock_no} className="flex items-center justify-between bg-white/[0.03] border border-white/5 p-4 rounded-xl">
                      <div>
                        <p className="font-medium">{stock.name}</p>
                        <p className="text-sm text-white/40">{stock.quantity}주 보유</p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleQuantityChange(stock.stock_no, -10, stock.name)}
                          className="px-4 py-2 bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg hover:bg-red-500/30 transition-all text-sm font-medium"
                        >
                          -10
                        </button>
                        <button
                          onClick={() => handleQuantityChange(stock.stock_no, 10, stock.name)}
                          className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 rounded-lg hover:bg-emerald-500/30 transition-all text-sm font-medium"
                        >
                          +10
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Changes */}
            <div className="bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">변경사항</h2>
                <button
                  onClick={() => setShowAddNew(true)}
                  className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-all text-sm"
                >
                  + 새 종목
                </button>
              </div>

              {changes.length === 0 ? (
                <p className="text-white/40 text-center py-8">위에서 수량을 조절해보세요</p>
              ) : (
                <div className="space-y-2 mb-4">
                  {changes.map((change, index) => (
                    <div key={index} className="flex items-center justify-between bg-white/[0.03] border border-white/5 p-3 rounded-xl">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{change.name}</span>
                        {change.quantity_delta && (
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${change.quantity_delta > 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                            {change.quantity_delta > 0 ? '+' : ''}{change.quantity_delta}주
                          </span>
                        )}
                        {change.quantity && (
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-500/20 text-blue-400">
                            신규 {change.quantity}주
                          </span>
                        )}
                      </div>
                      <button
                        onClick={() => removeChange(index)}
                        className="text-white/30 hover:text-red-400 transition-colors"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <button
                onClick={runSimulation}
                disabled={changes.length === 0 || simulating}
                className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-medium hover:from-purple-400 hover:to-pink-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {simulating ? '시뮬레이션 중...' : '시뮬레이션 실행'}
              </button>
            </div>
          </div>

          {/* Right: Results */}
          <div className="bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h2 className="text-lg font-semibold mb-4">시뮬레이션 결과</h2>

            {!result ? (
              <div className="text-center py-16">
                <div className="w-20 h-20 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-5">
                  <svg className="w-10 h-10 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <p className="text-white/30">변경사항을 추가하고</p>
                <p className="text-white/30">시뮬레이션을 실행해보세요</p>
              </div>
            ) : (
              <div className="space-y-5">
                {/* Before vs After */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                    <p className="text-white/40 text-xs tracking-widest uppercase mb-2">변경 전</p>
                    <p className="text-2xl font-light">{result.before.summary.total_value.toLocaleString()}<span className="text-white/40 text-sm ml-1">원</span></p>
                    <p className={`text-sm mt-1 ${result.before.summary.total_return >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {result.before.summary.total_return >= 0 ? '+' : ''}{result.before.summary.total_return}%
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-xl p-4">
                    <p className="text-white/40 text-xs tracking-widest uppercase mb-2">변경 후</p>
                    <p className="text-2xl font-light">{result.after.summary.total_value.toLocaleString()}<span className="text-white/40 text-sm ml-1">원</span></p>
                    <p className={`text-sm mt-1 ${result.after.summary.total_return >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {result.after.summary.total_return >= 0 ? '+' : ''}{result.after.summary.total_return}%
                    </p>
                  </div>
                </div>

                {/* Changes */}
                <div className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                  <p className="text-white/40 text-xs tracking-widest uppercase mb-3">변화량</p>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-white/40">투자금액</span>
                      <span className={result.diff.total_invested >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                        {result.diff.total_invested >= 0 ? '+' : ''}{result.diff.total_invested.toLocaleString()}원
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/40">평가금액</span>
                      <span className={result.diff.total_value >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                        {result.diff.total_value >= 0 ? '+' : ''}{result.diff.total_value.toLocaleString()}원
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/40">수익률</span>
                      <span className={result.diff.total_return >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                        {result.diff.total_return >= 0 ? '+' : ''}{result.diff.total_return}%p
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/40">종목 수</span>
                      <span className={result.diff.stock_count >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                        {result.diff.stock_count >= 0 ? '+' : ''}{result.diff.stock_count}개
                      </span>
                    </div>
                  </div>
                </div>

                {/* Risk with Explanation */}
                <div className="bg-white/[0.03] border border-white/5 rounded-xl p-4">
                  <p className="text-white/40 text-xs tracking-widest uppercase mb-3">리스크 분석</p>
                  
                  {/* 변동성 */}
                  <div className="mb-4 p-3 bg-white/[0.02] rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-white/60">변동성</span>
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-semibold">{result.after.risk.portfolio_volatility}%</span>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${getVolatilityInfo(result.after.risk.portfolio_volatility).color} bg-white/5`}>
                          {getVolatilityInfo(result.after.risk.portfolio_volatility).level}
                        </span>
                        <span className={`text-xs ${result.diff.portfolio_volatility <= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          ({result.diff.portfolio_volatility >= 0 ? '+' : ''}{result.diff.portfolio_volatility}%p)
                        </span>
                      </div>
                    </div>
                    <p className="text-white/40 text-xs">
                      {getVolatilityInfo(result.after.risk.portfolio_volatility).desc}
                    </p>
                  </div>

                  {/* 샤프비율 */}
                  <div className="p-3 bg-white/[0.02] rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-white/60">샤프비율</span>
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-semibold">{result.after.risk.sharpe_ratio}</span>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSharpeInfo(result.after.risk.sharpe_ratio).color} bg-white/5`}>
                          {getSharpeInfo(result.after.risk.sharpe_ratio).level}
                        </span>
                        <span className={`text-xs ${result.diff.sharpe_ratio >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          ({result.diff.sharpe_ratio >= 0 ? '+' : ''}{result.diff.sharpe_ratio})
                        </span>
                      </div>
                    </div>
                    <p className="text-white/40 text-xs">
                      {getSharpeInfo(result.after.risk.sharpe_ratio).desc}
                    </p>
                  </div>
                </div>

                {/* 투자 조언 */}
                <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-blue-400 mb-1">투자 조언</p>
                      <p className="text-white/60 text-xs leading-relaxed">
                        {result.after.risk.portfolio_volatility > 35 && result.after.risk.sharpe_ratio < 0.5 
                          ? '변동성이 높고 샤프비율이 낮습니다. ETF나 대형주 비중을 늘려 안정성을 높이는 것을 권장합니다.'
                          : result.after.risk.portfolio_volatility > 35
                          ? '변동성이 다소 높습니다. 분산투자를 통해 리스크를 줄이는 것을 고려해보세요.'
                          : result.after.risk.sharpe_ratio < 0.5
                          ? '위험 대비 수익률이 낮습니다. 수익성이 더 좋은 종목으로 교체를 고려해보세요.'
                          : result.after.risk.sharpe_ratio >= 1.0
                          ? '훌륭한 포트폴리오입니다! 현재 전략을 유지하면서 시장 상황을 모니터링하세요.'
                          : '적정 수준의 포트폴리오입니다. 꾸준한 리밸런싱으로 성과를 개선할 수 있습니다.'
                        }
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Add New Stock Modal */}
      {showAddNew && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowAddNew(false)}></div>
          <div className="relative bg-[#12121a] border border-white/10 rounded-2xl p-8 w-full max-w-md">
            <h3 className="text-xl font-semibold mb-6">새 종목 추가</h3>
            
            <div className="space-y-5">
              <div>
                <label className="block text-white/40 text-sm mb-2">종목 선택</label>
                <select
                  value={newStockNo || ''}
                  onChange={(e) => setNewStockNo(Number(e.target.value))}
                  className="w-full p-3 bg-white/[0.03] border border-white/10 rounded-xl text-white focus:outline-none focus:border-purple-500/50"
                >
                  <option value="">종목을 선택하세요</option>
                  {allStocks
                    .filter(s => !portfolioStocks.some(ps => ps.stock_no === s.stock_no))
                    .map((stock) => (
                      <option key={stock.stock_no} value={stock.stock_no}>
                        {stock.name} ({stock.symbol}) - {stock.current_price?.toLocaleString()}원
                      </option>
                    ))}
                </select>
              </div>

              <div>
                <label className="block text-white/40 text-sm mb-2">수량</label>
                <input
                  type="number"
                  value={newQuantity}
                  onChange={(e) => setNewQuantity(e.target.value)}
                  placeholder="매수 수량"
                  className="w-full p-3 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-purple-500/50"
                />
              </div>

              <div>
                <label className="block text-white/40 text-sm mb-2">매수가 (선택)</label>
                <input
                  type="number"
                  value={newPrice}
                  onChange={(e) => setNewPrice(e.target.value)}
                  placeholder="현재가로 자동 설정"
                  className="w-full p-3 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-purple-500/50"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-8">
              <button
                onClick={handleAddNewStock}
                className="flex-1 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl font-medium hover:from-purple-400 hover:to-pink-400 transition-all"
              >
                추가
              </button>
              <button
                onClick={() => setShowAddNew(false)}
                className="flex-1 py-3 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all"
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}