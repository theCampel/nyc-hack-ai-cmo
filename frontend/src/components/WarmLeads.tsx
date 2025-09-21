import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Eye, EyeOff, Linkedin, Phone, Mail, Users, Target } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Lead {
  id: string;
  name: string;
  title: string;
  company: string;
  avatar: string;
  phone: string;
  email: string;
  score: number;
  industry: string;
}

const mockLeads: Lead[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    title: 'VP of Marketing',
    company: 'TechFlow Inc.',
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b789?w=150&h=150&fit=crop&crop=face',
    phone: '+1 (555) 123-4567',
    email: 'sarah.chen@techflow.com',
    score: 95,
    industry: 'SaaS'
  },
  {
    id: '2',
    name: 'Michael Rodriguez',
    title: 'Chief Growth Officer',
    company: 'InnovateLabs',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
    phone: '+1 (555) 987-6543',
    email: 'm.rodriguez@innovatelabs.io',
    score: 92,
    industry: 'AI/ML'
  },
  {
    id: '3',
    name: 'Emily Thompson',
    title: 'Director of Digital Marketing',
    company: 'GrowthCorp',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
    phone: '+1 (555) 456-7890',
    email: 'emily.t@growthcorp.com',
    score: 88,
    industry: 'E-commerce'
  },
  {
    id: '4',
    name: 'David Kim',
    title: 'Head of Marketing Operations',
    company: 'ScaleUp Ventures',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
    phone: '+1 (555) 321-0987',
    email: 'david.kim@scaleup.vc',
    score: 90,
    industry: 'FinTech'
  }
];

export function WarmLeads() {
  const [revealedContacts, setRevealedContacts] = useState<{ [key: string]: { phone: boolean; email: boolean } }>({});

  const toggleContact = (leadId: string, type: 'phone' | 'email') => {
    setRevealedContacts(prev => ({
      ...prev,
      [leadId]: {
        ...prev[leadId],
        [type]: !prev[leadId]?.[type]
      }
    }));
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'bg-emerald-500/10 text-emerald-700 border-emerald-200';
    if (score >= 80) return 'bg-amber-500/10 text-amber-700 border-amber-200';
    return 'bg-slate-500/10 text-slate-700 border-slate-200';
  };

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center space-x-2 mb-2">
          
          <h2 className="text-3xl font-bold bg-gradient-to-r from-cmo-primary to-cmo-secondary bg-clip-text text-transparent">
            Warm Leads Identified
          </h2>
        </div>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Our AI has identified high-value prospects who match your ideal customer profile and are actively seeking solutions like yours.
        </p>
        <div className="flex items-center justify-center space-x-4 text-sm text-muted-foreground">
          <div className="flex items-center space-x-1">
            <Users className="w-4 h-4" />
            <span>{mockLeads.length} prospects found</span>
          </div>
          <div className="flex items-center space-x-1">
          </div>
        </div>
      </div>

      {/* Leads Grid */}
      <div className="grid gap-4">
        {mockLeads.map((lead, index) => (
          <Card 
            key={lead.id} 
            className={cn(
              "p-6 rounded-2xl bg-white/90 text-gray-900 backdrop-blur-xl",
              "border border-black/10 hover:border-cmo-primary/30 transition-all duration-300",
              "shadow-sm hover:shadow-lg hover:shadow-cmo-primary/10 group",
              "animate-fade-in-up"
            )}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                {/* Avatar & Basic Info */}
                <div className="relative">
                  <Avatar className="w-14 h-14 border-2 border-background shadow-lg">
                    <AvatarImage src={lead.avatar} alt={lead.name} />
                    <AvatarFallback className="bg-gradient-to-br from-cmo-primary/20 to-cmo-secondary/20 text-cmo-primary font-semibold">
                      {lead.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-[#0077b5] rounded-full flex items-center justify-center shadow-sm">
                    <Linkedin className="w-3 h-3 text-white" />
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3 mb-1">
                    <h3 className="font-semibold text-lg truncate">{lead.name}</h3>
                    
                  </div>
                  <p className="text-gray-700 font-medium">{lead.title}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-sm text-gray-600">{lead.company}</span>
                    <span className="w-1 h-1 bg-muted-foreground/40 rounded-full"></span>
                    <Badge variant="outline" className="text-xs text-gray-700 border-gray-300">
                      {lead.industry}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Contact Actions */}
              <div className="flex items-center space-x-2">
                {/* Phone */}
              <div className="flex items-center space-x-2">
                  {revealedContacts[lead.id]?.phone ? (
                    <div className="flex items-center space-x-2 px-3 py-2 bg-white/70 rounded-lg border border-gray-200 text-gray-800">
                      <Phone className="w-4 h-4 text-gray-600" />
                      <span className="text-sm font-mono">{lead.phone}</span>
                    </div>
                  ) : null}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => toggleContact(lead.id, 'phone')}
                    className={cn(
                      "border-cmo-primary/30 text-cmo-primary hover:bg-cmo-primary/5",
                      revealedContacts[lead.id]?.phone && "bg-cmo-primary/10"
                    )}
                  >
                    {revealedContacts[lead.id]?.phone ? (
                      <EyeOff className="w-4 h-4 mr-1" />
                    ) : (
                      <Eye className="w-4 h-4 mr-1" />
                    )}
                    {revealedContacts[lead.id]?.phone ? 'Hide' : 'Phone'}
                  </Button>
                </div>

                {/* Email */}
              <div className="flex items-center space-x-2">
                  {revealedContacts[lead.id]?.email ? (
                    <div className="flex items-center space-x-2 px-3 py-2 bg-white/70 rounded-lg border border-gray-200 text-gray-800">
                      <Mail className="w-4 h-4 text-gray-600" />
                      <span className="text-sm font-mono">{lead.email}</span>
                    </div>
                  ) : null}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => toggleContact(lead.id, 'email')}
                    className={cn(
                      "border-cmo-secondary/30 text-cmo-secondary hover:bg-cmo-secondary/5",
                      revealedContacts[lead.id]?.email && "bg-cmo-secondary/10"
                    )}
                  >
                    {revealedContacts[lead.id]?.email ? (
                      <EyeOff className="w-4 h-4 mr-1" />
                    ) : (
                      <Eye className="w-4 h-4 mr-1" />
                    )}
                    {revealedContacts[lead.id]?.email ? 'Hide' : 'Email'}
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-border/50">
        <div className="text-center">
          <div className="text-2xl font-bold text-cmo-primary">{mockLeads.length}</div>
          <div className="text-sm text-muted-foreground">Total Leads</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-cmo-secondary">
            {Math.round(mockLeads.reduce((acc, lead) => acc + lead.score, 0) / mockLeads.length)}%
          </div>
          <div className="text-sm text-muted-foreground">Avg. Match Score</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-emerald-600">
            {mockLeads.filter(lead => lead.score >= 90).length}
          </div>
          <div className="text-sm text-muted-foreground">High Priority</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-cmo-accent">4</div>
          <div className="text-sm text-muted-foreground">Industries</div>
        </div>
      </div>
    </div>
  );
}