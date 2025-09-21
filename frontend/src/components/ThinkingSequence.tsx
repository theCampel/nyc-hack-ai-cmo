import React, { useState, useEffect } from 'react';
import { Brain, Target, Video, Globe, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ThinkingSequenceProps {
  onComplete: () => void;
}

const thinkingSteps = [
  {
    icon: Brain,
    text: "Understanding company details...",
    duration: 2000,
  },
  {
    icon: Target,
    text: "Analyzing market positioning...",
    duration: 2500,
  },
  {
    icon: Video,
    text: "Composing UGC videos...",
    duration: 2200,
  },
  {
    icon: Globe,
    text: "Drafting landing pages...",
    duration: 2000,
  },
];

export function ThinkingSequence({ onComplete }: ThinkingSequenceProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (currentStep < thinkingSteps.length) {
      const timer = setTimeout(() => {
        setCurrentStep(currentStep + 1);
      }, thinkingSteps[currentStep].duration);

      return () => clearTimeout(timer);
    } else {
      setIsComplete(true);
      setTimeout(() => {
        onComplete();
      }, 1000);
    }
  }, [currentStep, onComplete]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-8">
      {/* Central Processing Orb */}
      <div className="relative">
        <div className="w-32 h-32 bg-gradient-to-br from-cmo-primary to-cmo-secondary rounded-full animate-pulse-glow flex items-center justify-center">
          <Sparkles className="w-16 h-16 text-primary-foreground animate-spin" style={{ animationDuration: '3s' }} />
        </div>
        
        {/* Orbiting Elements */}
        <div className="absolute inset-0 animate-spin" style={{ animationDuration: '8s' }}>
          {thinkingSteps.map((step, index) => {
            const angle = (index / thinkingSteps.length) * 360;
            const isActive = index <= currentStep;
            
            return (
              <div
                key={index}
                className={cn(
                  "absolute w-8 h-8 rounded-full flex items-center justify-center transition-all duration-500",
                  isActive 
                    ? "bg-cmo-accent text-primary-foreground scale-110" 
                    : "bg-muted text-muted-foreground scale-75"
                )}
                style={{
                  transform: `rotate(${angle}deg) translateY(-80px) rotate(-${angle}deg)`,
                }}
              >
                <step.icon className="w-4 h-4" />
              </div>
            );
          })}
        </div>
      </div>

      {/* Current Step Text */}
      <div className="text-center space-y-4 max-w-md">
        {currentStep < thinkingSteps.length ? (
          <div className="animate-fade-in-up">
            <h2 className="text-2xl font-semibold text-foreground mb-2">
              AI CMO is thinking...
            </h2>
            <p className="text-lg text-cmo-primary animate-thinking">
              {thinkingSteps[currentStep].text}
            </p>
          </div>
        ) : (
          <div className="animate-fade-in-up">
            <h2 className="text-2xl font-semibold text-cmo-primary mb-2">
              Ready to reveal your results!
            </h2>
            <p className="text-muted-foreground">
              Your AI CMO has crafted something amazing...
            </p>
          </div>
        )}
      </div>

      {/* Progress Indicator */}
      <div className="flex space-x-2">
        {thinkingSteps.map((_, index) => (
          <div
            key={index}
            className={cn(
              "w-3 h-3 rounded-full transition-all duration-300",
              index <= currentStep 
                ? "bg-cmo-primary scale-110" 
                : "bg-muted scale-75"
            )}
          />
        ))}
      </div>
    </div>
  );
}