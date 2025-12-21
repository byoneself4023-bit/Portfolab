import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { stockAPI, portfolioAPI } from '../api';

interface Stock {
  stock_no: number;
  symbol: string;
  name: string;
  market: string;
  current_price: number;
  sector_name: string | null;
}

interface Portfolio {
  portfolio_no: number;
  name: string;
  description: string;
}

export default function Home() {
  const navigate = useNavigate();
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const nickname = localStorage.getItem('nickname');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    loadData();
  }, [navigate]);

  const loadData = async () => {
    try {
      const [stockRes, portfolioRes] = await Promise.all([
        stockAPI.getList(),
        portfolioAPI.getList()
      ]);
      setStocks(stockRes.data.data || []);
      setPortfolios(portfolioRes.data.data || []);
    } catch (error) {
      console.error('데이터 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshPrices = async () => {
    setRefreshing(true);
    try {
      await fetch('https://port-0-flask-mjfnx06q4cbf889f.sel3.cloudtype.app/stock/update-prices', {
        method: 'POST'
      });
      await loadData();
    } catch (error) {
      console.error('가격 업데이트 실패:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('nickname');
    navigate('/login');
  };

  const filteredStocks = stocks.filter(stock =>
    stock.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    stock.symbol.includes(searchQuery)
  );

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

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-1/4 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-1/4 -right-1/4 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[120px]"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/5 rounded-full blur-[150px]"></div>
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50">
        <div className="absolute inset-0 bg-[#0a0a0f]/60 backdrop-blur-2xl border-b border-white/5"></div>
        <div className="relative max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
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
          </div>
          
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-3 px-4 py-2 bg-white/5 backdrop-blur-xl rounded-full border border-white/10">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-cyan-500 rounded-full flex items-center justify-center text-sm font-bold shadow-lg shadow-emerald-500/20">
                {nickname?.charAt(0).toUpperCase()}
              </div>
              <span className="text-sm text-white/80">{nickname}</span>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-white/40 hover:text-white text-sm transition-all hover:bg-white/5 rounded-lg"
            >
              로그아웃
            </button>
          </div>
        </div>
      </header>

      <main className="relative max-w-7xl mx-auto px-6 py-10">
        {/* Stats Cards */}
        <section className="mb-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Portfolio Card */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-cyan-500/30 transition-all duration-300">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-white/40 text-xs tracking-widest uppercase mb-3">Portfolios</p>
                    <p className="text-4xl font-light tracking-tight">{portfolios.length}</p>
                    <p className="text-white/30 text-sm mt-1">개 보유중</p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-xl flex items-center justify-center border border-cyan-500/20">
                    <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Stocks Card */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all duration-300">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-white/40 text-xs tracking-widest uppercase mb-3">Stocks</p>
                    <p className="text-4xl font-light tracking-tight">{stocks.length}</p>
                    <p className="text-white/30 text-sm mt-1">개 등록됨</p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl flex items-center justify-center border border-purple-500/20">
                    <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Status Card */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-emerald-500/30 transition-all duration-300">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-white/40 text-xs tracking-widest uppercase mb-3">Market</p>
                    <p className="text-4xl font-light tracking-tight text-emerald-400">Live</p>
                    <p className="text-white/30 text-sm mt-1">실시간 연동</p>
                  </div>
                  <div className="w-12 h-12 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-xl flex items-center justify-center border border-emerald-500/20">
                    <div className="relative">
                      <div className="w-3 h-3 bg-emerald-400 rounded-full"></div>
                      <div className="absolute inset-0 w-3 h-3 bg-emerald-400 rounded-full animate-ping"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Portfolios Section */}
        <section className="mb-12">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-lg font-semibold tracking-tight">내 포트폴리오</h2>
              <p className="text-white/30 text-sm">투자 포트폴리오를 관리하세요</p>
            </div>
            <Link
              to="/portfolio/create"
              className="group relative px-5 py-2.5 overflow-hidden rounded-xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-500"></div>
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-400 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <span className="relative font-medium text-sm">+ 새 포트폴리오</span>
            </Link>
          </div>

          {portfolios.length === 0 ? (
            <div className="bg-white/[0.02] backdrop-blur-xl border border-white/5 border-dashed rounded-2xl p-16 text-center">
              <div className="w-20 h-20 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-5">
                <svg className="w-10 h-10 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <p className="text-white/30 mb-2">아직 포트폴리오가 없습니다</p>
              <p className="text-white/20 text-sm mb-6">첫 번째 포트폴리오를 만들어보세요</p>
              <Link
                to="/portfolio/create"
                className="inline-block px-6 py-3 bg-white/10 hover:bg-white/20 rounded-xl transition-all text-sm"
              >
                포트폴리오 만들기
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {portfolios.map((portfolio) => (
                <Link
                  key={portfolio.portfolio_no}
                  to={`/portfolio/${portfolio.portfolio_no}`}
                  className="group relative"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  <div className="relative bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all duration-300">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-xl flex items-center justify-center">
                        <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <svg className="w-5 h-5 text-white/20 group-hover:text-white/50 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                    <h3 className="font-semibold mb-1 group-hover:text-cyan-400 transition-colors">{portfolio.name}</h3>
                    <p className="text-white/30 text-sm line-clamp-2">{portfolio.description || '설명 없음'}</p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>

        {/* Stocks Section */}
        <section>
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
            <div>
              <h2 className="text-lg font-semibold tracking-tight">종목 목록</h2>
              <p className="text-white/30 text-sm">실시간 주식 시세</p>
            </div>
            <div className="flex items-center gap-3 w-full md:w-auto">
              <div className="relative flex-1 md:w-72">
                <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  type="text"
                  placeholder="종목명 또는 코드 검색"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-white/[0.03] border border-white/10 rounded-xl focus:outline-none focus:border-cyan-500/50 text-white placeholder-white/30 text-sm transition-all"
                />
              </div>
              <button
                onClick={handleRefreshPrices}
                disabled={refreshing}
                className="flex items-center gap-2 px-5 py-3 bg-white/[0.03] border border-white/10 rounded-xl hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-all disabled:opacity-50 text-sm whitespace-nowrap"
              >
                <svg className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span className={refreshing ? 'text-white/50' : 'text-emerald-400'}>
                  {refreshing ? '업데이트중' : '시세 새로고침'}
                </span>
              </button>
            </div>
          </div>

          <div className="bg-white/[0.02] backdrop-blur-xl border border-white/5 rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="px-6 py-4 text-left text-white/40 font-normal text-xs tracking-widest uppercase">종목명</th>
                    <th className="px-6 py-4 text-left text-white/40 font-normal text-xs tracking-widest uppercase">코드</th>
                    <th className="px-6 py-4 text-left text-white/40 font-normal text-xs tracking-widest uppercase">시장</th>
                    <th className="px-6 py-4 text-left text-white/40 font-normal text-xs tracking-widest uppercase">섹터</th>
                    <th className="px-6 py-4 text-right text-white/40 font-normal text-xs tracking-widest uppercase">현재가</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStocks.map((stock) => (
                    <tr 
                      key={stock.stock_no} 
                      className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors"
                    >
                      <td className="px-6 py-4">
                        <span className="font-medium">{stock.name}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-white/40 font-mono text-sm">{stock.symbol}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${
                          stock.market === 'KOSPI' 
                            ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' 
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        }`}>
                          {stock.market}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-white/40 text-sm">{stock.sector_name || '-'}</td>
                      <td className="px-6 py-4 text-right">
                        <span className="text-lg font-semibold tabular-nums">
                          {stock.current_price?.toLocaleString()}
                        </span>
                        <span className="text-white/30 text-sm ml-1">원</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {filteredStocks.length === 0 && (
              <div className="py-16 text-center text-white/30">
                검색 결과가 없습니다
              </div>
            )}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative border-t border-white/5 mt-20">
        <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-white/20 text-sm">© 2024 PortfoLab. Investment Simulation Platform</p>
          <div className="flex items-center gap-6 text-white/20 text-sm">
            <span>한국투자증권 API 연동</span>
            <span>•</span>
            <span>실시간 시세</span>
          </div>
        </div>
      </footer>
    </div>
  );
}