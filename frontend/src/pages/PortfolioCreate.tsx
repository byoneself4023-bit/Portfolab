import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { portfolioAPI } from '../api';

export default function PortfolioCreate() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await portfolioAPI.create({ name, description });
      if (response.data.success) {
        navigate('/');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || '포트폴리오 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

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

      <main className="relative max-w-2xl mx-auto px-6 py-16">
        <div className="text-center mb-10">
          <div className="w-16 h-16 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/10">
            <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold mb-2">새 포트폴리오 만들기</h1>
          <p className="text-white/40">나만의 투자 포트폴리오를 생성하세요</p>
        </div>

        <div className="bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-2xl p-8">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-xl mb-6 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-white/40 text-sm mb-2">포트폴리오 이름</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="예: 성장주 포트폴리오"
                className="w-full p-4 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-cyan-500/50 transition-all"
                required
              />
            </div>

            <div>
              <label className="block text-white/40 text-sm mb-2">설명 (선택)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="포트폴리오에 대한 설명을 입력하세요"
                rows={4}
                className="w-full p-4 bg-white/[0.03] border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-cyan-500/50 transition-all resize-none"
              />
            </div>

            <div className="flex gap-4 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl font-medium hover:from-cyan-400 hover:to-blue-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    생성 중...
                  </span>
                ) : '포트폴리오 생성'}
              </button>
              <Link
                to="/"
                className="flex-1 py-4 bg-white/5 border border-white/10 rounded-xl text-center hover:bg-white/10 transition-all"
              >
                취소
              </Link>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}