import React, { useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Play, ExternalLink, Download, Share, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import sampleVideo from '@/assets/Final.mp4';
import siteThumb from '@/assets/site.png';
import { WarmLeads } from '@/components/WarmLeads';

interface ResultsRevealProps {
  onReset: () => void;
}

export function ResultsReveal({ onReset }: ResultsRevealProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  return (
    <div className="w-full max-w-6xl mx-auto space-y-8 animate-fade-in-up">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-2 mb-4">
          
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cmo-primary to-cmo-secondary bg-clip-text text-transparent">
            Your AI CMO Results
          </h1>
          
        </div>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Your personalised marketing strategy is ready. Here's what your AI CMO has created for you.
        </p>
      </div>

      {/* Results Grid */}
      <div className="grid md:grid-cols-2 gap-8">
        {/* Video Preview */}
        <Card className="group overflow-hidden border-border/50 hover:border-cmo-primary/50 transition-all duration-500 hover:shadow-2xl hover:shadow-cmo-primary/10">
          <div className="aspect-video bg-black relative overflow-hidden">
            <video
              ref={videoRef}
              src={sampleVideo}
              className="absolute inset-0 w-full h-full object-contain"
              controls
              playsInline
            />
          </div>

          <div className="p-6 space-y-4">
            <div>
              <h3 className="text-xl font-semibold mb-2">Generated Video Content</h3>
              <p className="text-muted-foreground">
                Custom UGC-style videos tailored to your brand voice and target audience.
              </p>
            </div>
            
            <div className="flex space-x-2">
              <Button className="flex-1 bg-cmo-primary hover:bg-cmo-primary/90" onClick={() => videoRef.current?.play()}>
                <Play className="w-4 h-4 mr-2" />
                Watch Preview
              </Button>
              <Button variant="outline" size="icon" asChild>
                <a href={sampleVideo} download>
                  <Download className="w-4 h-4" />
                </a>
              </Button>
              <Button variant="outline" size="icon">
                <Share className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>

        {/* Website Preview */}
        <Card className="group overflow-hidden border-border/50 hover:border-cmo-primary/50 transition-all duration-500 hover:shadow-2xl hover:shadow-cmo-primary/10">
          <div className="aspect-video bg-gradient-to-br from-background to-muted relative overflow-hidden">
            {/* Website Screenshot Preview */}
            <a href="https://awesome-hub-910.10web.cloud/" target="_blank" rel="noopener noreferrer">
              <img src={siteThumb} alt="Custom Landing Page Preview" className="absolute inset-0 w-full h-full object-cover" />
            </a>
            {/* Overlay on hover */}
            <div className="absolute inset-0 bg-cmo-secondary/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </div>
          
          <div className="p-6 space-y-4">
            <div>
              <h3 className="text-xl font-semibold mb-2">Custom Landing Page</h3>
              <p className="text-muted-foreground">
                A conversion-optimized landing page designed specifically for your business.
              </p>
            </div>
            
            <div className="flex space-x-2">
              <Button className="flex-1 bg-cmo-secondary hover:bg-cmo-secondary/90" asChild>
                <a href="https://awesome-hub-910.10web.cloud/" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Visit Site
                </a>
              </Button>
              <Button variant="outline" size="icon">
                <Download className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Share className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Warm Leads Section */}
      <div className="mt-12">
        <WarmLeads />
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
        <Button 
          size="lg"
          className={cn(
            "px-8 py-3 bg-gradient-to-r from-cmo-primary to-cmo-secondary text-primary-foreground",
            "hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl"
          )}
        >
          <Sparkles className="w-5 h-5 mr-2" />
          Generate More Content
        </Button>
        
        <Button 
          variant="outline" 
          size="lg"
          onClick={onReset}
          className="px-8 py-3 border-cmo-primary/30 text-cmo-primary hover:bg-cmo-primary/5"
        >
          Start New Project
        </Button>
      </div>
    </div>
  );
}