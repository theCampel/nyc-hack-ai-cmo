import React, { useState } from 'react';
import { FileUpload } from '@/components/FileUpload';
import { HireCMOButton } from '@/components/HireCMOButton';
import { ThinkingSequence } from '@/components/ThinkingSequence';
import { ResultsReveal } from '@/components/ResultsReveal';
import { useIsMobile } from '@/hooks/use-mobile';
import bgImage from '@/assets/bg3.png';

interface UploadedFile {
  id: string;
  file: File;
  type: 'photo' | 'document';
  preview?: string;
}

type AppState = 'upload' | 'thinking' | 'results';

const Index = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [appState, setAppState] = useState<AppState>('upload');
  const [isLoading, setIsLoading] = useState(false);
  const isMobile = useIsMobile();

  const hasPhoto = files.some(file => file.type === 'photo');
  
  // Responsive sizing for background orb
  const orbWidth = isMobile ? '260%' : '190%';

  const handleFilesChange = (newFiles: UploadedFile[]) => {
    setFiles(newFiles);
  };

  const handleHireCMO = () => {
    if (!hasPhoto) return;
    
    setIsLoading(true);
    setAppState('thinking');
  };

  const handleThinkingComplete = () => {
    setIsLoading(false);
    setAppState('results');
  };

  const handleReset = () => {
    setFiles([]);
    setAppState('upload');
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* 7-Layer Background System */}
      <div className="fixed inset-0 w-full overflow-hidden">
        {/* Layer -1: Full-screen white underlay to prevent any dark top bar */}
        <div className="absolute inset-0 bg-white" />
        {/* Layer 0: White Background Base */}
        <div 
          className="absolute left-1/2 aspect-square overflow-hidden orb-mask orb-performance"
          style={{
            width: orbWidth,
            transform: 'translateX(-50%)',
            background: 'white'
          }}
        />
        
        {/* Layer 1: Primary Background Image (bg3.png orb) */}
        <div 
          className="absolute left-1/2 aspect-square overflow-hidden orb-mask orb-performance"
          style={{
            width: orbWidth,
            transform: 'translateX(-50%)',
            backgroundImage: `url(${bgImage})`,
            backgroundSize: 'cover',
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'center top'
          }}
        />
        
        {/* Layer 2 & 3: Gradient Overlay Container with Blur */}
        <div 
          className="absolute inset-0 mt-0 opacity-100"
          style={{ filter: 'blur(10px)' }}
        >
          {/* Layer 3: Radial Gradient Overlay */}
          <div
            className="absolute left-1/2 aspect-square overflow-hidden transition-all duration-700 ease-out orb-mask orb-performance"
            style={{
              width: orbWidth,
              transform: 'translateX(-50%)',
              background: 'radial-gradient(ellipse at center, hsl(270 100% 80% / 0.15) 0%, hsl(280 100% 70% / 0.08) 50%, transparent 70%)'
            }}
          />
          
          {/* Layer 4: Muting Veil for Text Contrast */}
          <div
            className="absolute inset-0"
            style={{
              background: 'radial-gradient(ellipse at center, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0.4) 35%, rgba(255,255,255,0.15) 60%, transparent 75%)'
            }}
          />
        </div>
        
        {/* Layer 5: Grain/Noise Texture */}
        <div className="absolute inset-0 opacity-20 grain-texture" />
      </div>
      
      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        {appState === 'upload' && (
          <header className="pt-16 pb-12">
            <div className="container mx-auto px-6 text-center">
              {/* Brand/Logo */}
              <div className="mb-8 text-sm font-semibold text-gray-600 tracking-wide uppercase animate-fade-in-up">
                AI Chief Marketing Officer
              </div>
              
              <h1 className="text-4xl md:text-6xl lg:text-7xl font-normal leading-tight mb-6 text-gray-900 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                Human-Level Marketing,{' '}
                <span className="font-semibold bg-gradient-to-r from-purple-600 to-purple-500 bg-clip-text text-transparent">
                  Instantly
                </span>
              </h1>
              <p className="text-lg md:text-xl text-gray-700 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                From launch-website to user-generated content, lead generator to SEO optimiser, our AI Chief Marketing Officer will help you grow your business from day one. 
              </p>
            </div>
          </header>
        )}

        {/* Main Content */}
        <main className="container mx-auto px-6">
          {appState === 'upload' && (
            <div className="max-w-4xl mx-auto space-y-12">
              {/* Upload Section */}
              <div className="animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
                <FileUpload 
                  onFilesChange={handleFilesChange}
                  hasPhoto={hasPhoto}
                />
              </div>

              {/* Hire CMO Button */}
              <div className="flex justify-center animate-fade-in-up" style={{ animationDelay: '0.6s' }}>
                <HireCMOButton
                  isEnabled={hasPhoto}
                  isLoading={isLoading}
                  onClick={handleHireCMO}
                  filesCount={files.length}
                />
              </div>

              {/* Features Grid */}
              <div className="grid md:grid-cols-3 gap-8 pt-16 animate-fade-in-up" style={{ animationDelay: '0.8s' }}>
                <div className="text-center space-y-5 p-8 rounded-3xl bg-white/90 backdrop-blur-xl border border-black/10 shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-14 h-14 bg-white rounded-full border border-black/10 shadow-sm flex items-center justify-center mx-auto">
                    <div className="w-4 h-4 rounded bg-gradient-to-r from-cmo-primary to-cmo-secondary" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">Launch Website Creator</h3>
                  <p className="text-base text-gray-700 leading-relaxed max-w-xs mx-auto">
                    We'll create a beautiful website for your business, to prepare you for a viral launch.
                  </p>
                </div>

                <div className="text-center space-y-5 p-8 rounded-3xl bg-white/90 backdrop-blur-xl border border-black/10 shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-14 h-14 bg-white rounded-full border border-black/10 shadow-sm flex items-center justify-center mx-auto">
                    <div className="w-4 h-4 rounded-full bg-gradient-to-r from-cmo-primary to-cmo-secondary" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">User Generated Content</h3>
                  <p className="text-base text-gray-700 leading-relaxed max-w-xs mx-auto">
                    Create swarms of users promoting your product or service, ready for social media.
                  </p>
                </div>

                <div className="text-center space-y-5 p-8 rounded-3xl bg-white/90 backdrop-blur-xl border border-black/10 shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-14 h-14 bg-white rounded-full border border-black/10 shadow-sm flex items-center justify-center mx-auto">
                    <div className="w-4 h-4 rounded-lg bg-gradient-to-r from-cmo-primary to-cmo-secondary" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">Find Leads, Immediately</h3>
                  <p className="text-base text-gray-700 leading-relaxed max-w-xs mx-auto">
                    Recieve instant leads for your business, ready to be converted into customers.
                  </p>
                </div>
              </div>
            </div>
          )}

          {appState === 'thinking' && (
            <ThinkingSequence onComplete={handleThinkingComplete} />
          )}

          {appState === 'results' && (
            <div className="py-8">
              <ResultsReveal onReset={handleReset} />
            </div>
          )}
        </main>

        {/* Footer */}
        {appState === 'upload' && (
          <footer className="pt-24 pb-8 text-center">
            <p className="text-sm text-gray-500 animate-fade-in-up" style={{ animationDelay: '1s' }}>
              
            </p>
          </footer>
        )}
      </div>
    </div>
  );
};

export default Index;
