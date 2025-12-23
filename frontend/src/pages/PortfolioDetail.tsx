import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { portfolioAPI, stockAPI } from '../api';

interface Stock {
  stock_no: number;
  symbol: string;
  name: string;
  market: string;
  current_price: number;
}

interface PortfolioStock {
  portfolio_stock_no: number;
  stock_no: number;
  symbol: string;
  name: string;
  quantity: number;
  avg_price: number;
  current_price: number;
}

interface Portfolio {
  portfolio_no: number;
  name: string;
  description: string;
}

export default function PortfolioDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const portfolioNo = Number(id);

  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [portfolioStocks, setPortfolioStocks] = useState<PortfolioStock[]>([]);
  const [allStocks, setAllStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedStock, setSelectedStock] = useState<number | null>(null);
  const [quantity, setQuantity] = useState('');
  const [avgPrice, setAvgPrice] = useState('');

  useEffect(() => {
    loadData();
  }, [portfolioNo]);

  const loadData = async () => {
    try {
      const [portfolioRes, stocksRes, allStocksRes] = await Promise.all([
        portfolioAPI.getDetail(portfolioNo),
        portfolioAPI.getStocks(portfolioNo),
        stockAPI.getList()
      ]);
      setPortfolio(portfolioRes.data.data);
      setPortfolioStocks(stocksRes.data.data?.stocks || []);
      setAllStocks(allStocksRes.data.data || []);
    } catch (error) {
      console.error('데이터 로딩 실패:', error);
      setPortfolioStocks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddStock = async () => {
    if (!selectedStock || !quantity || !avgPrice) {
      alert('모든 항목을 입력해주세요.');
      return;
    }
    try {
      await portfolioAPI.addStock(portfolioNo, {
        stock_no: selectedStock,
        quantity: Number(quantity),
        avg_price: Number(avgPrice)
      });
      setShowAddModal(false);
      setSelectedStock(null);
      setQuantity('');
      setAvgPrice('');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.message || '종목 추가에 실패했습니다.');
    }
  };

  const handleRemoveStock = async (stockNo: number) => {
    if (!confirm('이 종목을 삭제하시겠습니까?')) return;
    try {
      await portfolioAPI.removeStock(portfolioNo, stockNo);
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.message || '종목 삭제에 실패했습니다.');
    }
  };

  const handleDeletePortfolio = async () => {
    if (!confirm('이 포트폴리오를 삭제하시겠습니까?')) return;
    try {
      await portfolioAPI.delete(portfolioNo);
      navigate('/');
    } catch (error: any) {
      alert(error.response?.data?.message || '포트폴리오 삭제에 실패했습니다.');
    }
  };

  const calculateReturn = (stock: PortfolioStock) => {
    if (!stock.current_price || !stock.avg_price) return 0;
    return ((stock.current_price - stock.avg_price) / stock.avg_price) * 100;
  };

  const totalInvestment = portfolioStocks.reduce(
    (sum, stock) => sum + stock.quantity * stock.avg_price, 0
  );

  const totalValue = portfolioStocks.reduce(
    (sum, stock) => sum + stock.quantity * (stock.current_price || stock.avg_price), 0
  );

  const totalReturn = totalInvestment > 0 
    ? ((totalValue - totalInvestment) / totalInvestment) * 100 
    : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-2 border-white/20 border-t-cyan-400 rounded-full animate-spin"></div>
          <p className="text-white/50 text-sm tracking-widest uppercase">Loading</p>
        </div>
      </div>
    );
  }

  if (!portfolio) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-white/50">포트폴리오를 찾을 수 없습니다.</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-1/4 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-1/4 -right-1/4 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[120px]"></div>
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50">
        <div className="absolute inset-0 bg-[#0a0a0f]/60 backdrop-blur-2xl border-b border-white/5"></div>
        <div className="relative max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl blur-lg opacity-50"></div>
              <div className="relative w-11 h-11 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-xl flex items-center justify-center">
                <span className="text-xl font-black">P</span>
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">PortfoLab</h1>
              <p className="text-[10px] text-white/40 tracking-[0.2em] uppercase">Investment Simulator</p>
            </div>
          </Link>
          <Link to="/" className="text-white/40 hover:text-white text-sm transition-all hover:bg-white/5 px-4 py-2 rounded-lg">
            ← 홈으로
          </Link>
        </div>
      </header>

      <main className="relative max-w-7xl mx-auto px-6 py-10">
        {/* Portfolio Header */}
        <div className="bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-8 mb-8">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div>
              <h1 className="text-3xl font-bold mb-2">{portfolio.name}</h1>
              <p className="text-white/40">{portfolio.description || '설명 없음'}</p>
            </div>
            <div className="flex gap-3">
              <Link
                to={`/portfolio/${portfolioNo}/simulation`}
                className="group relative px-5 py-2.5 overflow-hidden rounded-xl"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-purple-400 to-pink-400 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <span className="relative font-medium text-sm">시뮬레이션</span>
              </Link>
              <button
                onClick={handleDeletePortfolio}
                className="px-5 py-2.5 bg-red-500/20 border border-red-500/30 text-red-400 rounded-xl hover:bg-red-500/30 transition-all text-sm"
              >
                삭제
              </button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="bg-white/[0.03] border border-white/5 rounded-xl p-5">
              <p className="text-white/40 text-xs tracking-widest uppercase mb-2">총 투자금액</p>
              <p className="text-2xl font-light">{totalInvestment.toLocaleString()}<span className="text-white/40 text-sm ml-1">원</span></p>
            </div>
            <div className="bg-white/[0.03] border border-white/5 rounded-xl p-5">
              <p className="text-white/40 text-xs tracking-widest uppercase mb-2">총 평가금액</p>
              <p className="text-2xl font-light">{totalValue.toLocaleString()}<span className="text-white/40 text-sm ml-1">원</span></p>
            </div>
            <div className="bg-white/[0.03] border border-white/5 rounded-xl p-5">
              <p className="text-white/40 text-xs tracking-widest uppercase mb-2">총 수익률</p>
              <p className={`text-2xl font-light ${totalReturn >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {totalReturn >= 0 ? '+' : ''}{totalReturn.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>

        {/* Holdings */}
        <div className="bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-8">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-lg font-semibold">보유 종목</h2>
              <p className="text-white/30 text-sm">포트폴리오에 담긴 종목들</p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="group relative px-5 py-2.5 overflow-hidden rounded-xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-500"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-400 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <span className="relative font-medium text-sm">+ 종목 추가</span>
            </button>
          </div>

          {portfolioStocks.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-20 h-20 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-5">
                <svg className="w-10 h-10 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <p className="text-white/30 mb-2">아직 보유 종목이 없습니다</p>
              <p className="text-white/20 text-sm">종목을 추가해보세요</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="px-4 py-3 text-left text-white/40 font-normal text-xs tracking-widest uppercase">종목</th>
                    <th className="px-4 py-3 text-right text-white/40 font-normal text-xs tracking-widest uppercase">수량</th>
                    <th className="px-4 py-3 text-right text-white/40 font-normal text-xs tracking-widest uppercase">매수가</th>
                    <th className="px-4 py-3 text-right text-white/40 font-normal text-xs tracking-widest uppercase">현재가</th>
                    <th className="px-4 py-3 text-right text-white/40 font-normal text-xs tracking-widest uppercase">평가금액</th>
                    <th className="px-4 py-3 text-right text-white/40 font-normal text-xs tracking-widest uppercase">수익률</th>
                    <th className="px-4 py-3 text-center text-white/40 font-normal text-xs tracking-widest uppercase"></th>
                  </tr>
                </thead>
                <tbody>
                  {portfolioStocks.map((stock) => {
                    const returnRate = calculateReturn(stock);
                    const evalValue = stock.quantity * (stock.current_price || stock.avg_price);
                    return (
                      <tr key={stock.portfolio_stock_no} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                        <td className="px-4 py-4">
                          <p className="font-medium">{stock.name}</p>
                          <p className="text-white/40 text-sm font-mono">{stock.symbol}</p>
                        </td>
                        <td className="px-4 py-4 text-right tabular-nums">{stock.quantity.toLocaleString()}<span className="text-white/40 ml-1">주</span></td>
                        <td className="px-4 py-4 text-right tabular-nums">{stock.avg_price.toLocaleString()}<span className="text-white/40 ml-1">원</span></td>
                        <td className="px-4 py-4 text-right tabular-nums">{(stock.current_price || 0).toLocaleString()}<span className="text-white/40 ml-1">원</span></td>
                        <td className="px-4 py-4 text-right tabular-nums font-medium">{evalValue.toLocaleString()}<span className="text-white/40 ml-1">원</span></td>
                        <td className={`px-4 py-4 text-right font-medium ${returnRate >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {returnRate >= 0 ? '+' : ''}{returnRate.toFixed(2)}%
                        </td>
                        <td className="px-4 py-4 text-center">
                          <button
                            onClick={() => handleRemoveStock(stock.stock_no)}
                            className="text-white/30 hover:text-red-400 transition-colors"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* Add Stock Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowAddModal(false)}></div>
          <div className="relative bg-[#12121a] border border-white/10 rounded-2xl p-8 w-full max-w-md">
            <h3 className="text-xl font-semibold mb-6">종목 추가</h3>
            
            <div className="space-y-5">
              <div>
                <label className="block text-white/40 text-sm mb-2">종목 선택</label>
                <select
                  value={selectedStock || ''}
                  onChange={(e) => setSelectedStock(Number(e.target.value))}
                  className="w-full p-3 bg-white/[0.03] border border-white/10 rounded-xl text-white focus:outline-none focus:border-cyan-500/50"
                >
                  <option value="">종목을 선택하세요</option>
                  {allStocks.map((stock) => (
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
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  placeholder="보유 수량"
                  className="w-full p-3 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-cyan-500/50"
                />
              </div>

              <div>
                <label className="block text-white/40 text-sm mb-2">매수 평균가</label>
                <input
                  type="number"
                  value={avgPrice}
                  onChange={(e) => setAvgPrice(e.target.value)}
                  placeholder="매수 평균 가격"
                  className="w-full p-3 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-cyan-500/50"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-8">
              <button
                onClick={handleAddStock}
                className="flex-1 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl font-medium hover:from-cyan-400 hover:to-blue-400 transition-all"
              >
                추가
              </button>
              <button
                onClick={() => setShowAddModal(false)}
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