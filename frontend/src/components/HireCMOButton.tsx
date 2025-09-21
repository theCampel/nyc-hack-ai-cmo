import React from 'react';
import { Button } from '@/components/ui/button';
import { Sparkles, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HireCMOButtonProps {
  isEnabled: boolean;
  isLoading: boolean;
  onClick: () => void;
  filesCount: number;
}

export function HireCMOButton({ isEnabled, isLoading, onClick, filesCount }: HireCMOButtonProps) {
  return (
    <div className="relative flex flex-col items-center space-y-6">
      {/* File Count Indicator */}
      {filesCount > 0 && (
        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
          <div className="w-2 h-2 bg-cmo-primary rounded-full animate-pulse" />
          <span>{filesCount} file{filesCount > 1 ? 's' : ''} attached</span>
        </div>
      )}

      {/* Main Button */}
      <Button
        onClick={onClick}
        disabled={!isEnabled || isLoading}
        size="lg"
        className={cn(
          "relative px-8 py-4 text-lg font-semibold rounded-full transition-all duration-300 transform",
          "border border-white/30 backdrop-blur-xl",
          isEnabled 
            ? "bg-white/15 text-gray-900 hover:bg-white/20 hover:scale-105 hover:shadow-xl hover:border-white/50"
            : "bg-white/10 text-gray-500 cursor-not-allowed border-white/20",
          isLoading && "animate-pulse"
        )}
        style={{
          backdropFilter: 'blur(12px) saturate(160%)',
          WebkitBackdropFilter: 'blur(12px) saturate(160%)',
          boxShadow: isEnabled ? '0 10px 30px rgba(0,0,0,0.1)' : '0 4px 15px rgba(0,0,0,0.05)'
        }}
      >
        <div className="flex items-center space-x-3">
          {isLoading ? (
            <Loader2 className="w-6 h-6 animate-spin" />
          ) : (
            <Sparkles className={cn(
              "w-6 h-6 transition-all duration-300",
              isEnabled && "animate-pulse"
            )} />
          )}
          <span>
            {isLoading ? 'Processing...' : 'Get Started'}
          </span>
        </div>

        {/* Glow Effect */}
        {isEnabled && !isLoading && (
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cmo-primary/20 to-cmo-secondary/20 blur-xl animate-pulse-glow -z-10" />
        )}
      </Button>

      {/* Status Text */}
      <p className={cn(
        "text-sm transition-all duration-300",
        isEnabled 
          ? "text-gray-700 animate-fade-in-up" 
          : "text-gray-500"
      )}>
        {isEnabled 
          ? "Ready to transform your marketing strategy"
          : "Upload your photo to get started"
        }
      </p>
    </div>
  );
}