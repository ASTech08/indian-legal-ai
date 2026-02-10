'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  Scale, 
  MessageSquare, 
  FileText, 
  Search, 
  Shield, 
  Zap,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  BookOpen,
  Building2,
  Users,
  TrendingUp
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const features = [
  {
    icon: MessageSquare,
    title: 'Conversational Legal AI',
    description: 'Ask any question about Indian law and get accurate, source-backed answers instantly.',
  },
  {
    icon: FileText,
    title: 'Document Analysis',
    description: 'Upload contracts, FIRs, legal notices, and get comprehensive analysis with risk assessment.',
  },
  {
    icon: Search,
    title: 'Deep Case Research',
    description: 'Search through thousands of Indian judgments with AI-powered relevance ranking.',
  },
  {
    icon: Shield,
    title: 'Legal Drafting',
    description: 'Generate court-ready legal documents, petitions, notices, and contracts in minutes.',
  },
  {
    icon: Building2,
    title: 'Corporate Compliance',
    description: 'Stay compliant with labour laws, Companies Act, and corporate regulations.',
  },
  {
    icon: TrendingUp,
    title: 'Outcome Prediction',
    description: 'Simulate case outcomes based on past precedents and judicial trends.',
  },
]

const useCases = [
  {
    icon: Users,
    title: 'For Lawyers',
    description: 'Save hours on research, draft documents faster, and find relevant precedents instantly.',
    benefits: ['Case law research', 'Document drafting', 'Client consultations', 'Court preparation'],
  },
  {
    icon: Building2,
    title: 'For Corporates',
    description: 'Ensure compliance, review contracts, and manage legal risks proactively.',
    benefits: ['Contract review', 'Labour compliance', 'Risk assessment', 'Policy drafting'],
  },
  {
    icon: BookOpen,
    title: 'For Citizens',
    description: 'Understand legal documents, know your rights, and navigate legal processes confidently.',
    benefits: ['Document understanding', 'Legal awareness', 'FIR drafting', 'Rights information'],
  },
]

const stats = [
  { label: 'Case Laws Indexed', value: '1M+' },
  { label: 'Bare Acts Covered', value: '500+' },
  { label: 'Documents Analyzed', value: '100K+' },
  { label: 'Active Users', value: '10K+' },
]

export default function LandingPage() {
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null)

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/20">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 backdrop-blur-lg bg-background/80 border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Scale className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold gradient-text">Indian Legal AI</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <Link href="#features" className="text-sm font-medium hover:text-primary transition-colors">
                Features
              </Link>
              <Link href="#use-cases" className="text-sm font-medium hover:text-primary transition-colors">
                Use Cases
              </Link>
              <Link href="#pricing" className="text-sm font-medium hover:text-primary transition-colors">
                Pricing
              </Link>
              <Link href="/docs" className="text-sm font-medium hover:text-primary transition-colors">
                Docs
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/sign-in">
                <Button variant="ghost">Sign In</Button>
              </Link>
              <Link href="/sign-up">
                <Button>
                  Get Started <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 pt-20 pb-32">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-4xl mx-auto"
        >
          <div className="inline-flex items-center space-x-2 bg-primary/10 text-primary px-4 py-2 rounded-full mb-6">
            <Sparkles className="h-4 w-4" />
            <span className="text-sm font-medium">AI-Powered Legal Intelligence for India</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-foreground via-foreground to-foreground/60">
            Your AI Legal Assistant for Indian Law
          </h1>
          
          <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-3xl mx-auto">
            Research case laws, analyze documents, draft legal papers, and get AI-powered insights —
            all trained on Indian judiciary, bare acts, and court judgments.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <Link href="/chat">
              <Button size="lg" className="text-lg px-8 py-6">
                <MessageSquare className="mr-2 h-5 w-5" />
                Start Chatting
              </Button>
            </Link>
            <Link href="#demo">
              <Button size="lg" variant="outline" className="text-lg px-8 py-6">
                Watch Demo
              </Button>
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-3xl mx-auto">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold text-primary mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Powerful Features for Legal Professionals
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to research, analyze, and draft legal documents with AI assistance
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              onMouseEnter={() => setHoveredFeature(index)}
              onMouseLeave={() => setHoveredFeature(null)}
            >
              <Card className="h-full transition-all duration-300 hover:shadow-xl hover:scale-105 border-2 hover:border-primary/50">
                <CardHeader>
                  <div className={`h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 transition-transform duration-300 ${hoveredFeature === index ? 'scale-110' : ''}`}>
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Use Cases Section */}
      <section id="use-cases" className="container mx-auto px-4 py-20 bg-muted/20">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Built for Everyone in the Legal Ecosystem
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            From lawyers to citizens, our platform adapts to your legal needs
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {useCases.map((useCase, index) => (
            <motion.div
              key={useCase.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="h-full">
                <CardHeader>
                  <div className="h-14 w-14 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                    <useCase.icon className="h-7 w-7 text-primary" />
                  </div>
                  <CardTitle className="text-2xl">{useCase.title}</CardTitle>
                  <CardDescription className="text-base">
                    {useCase.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {useCase.benefits.map((benefit) => (
                      <li key={benefit} className="flex items-start">
                        <CheckCircle2 className="h-5 w-5 text-primary mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{benefit}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="bg-gradient-to-r from-primary to-primary/80 rounded-3xl p-12 md:p-16 text-center text-white"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Transform Your Legal Work?
          </h2>
          <p className="text-xl mb-10 max-w-2xl mx-auto opacity-90">
            Join thousands of legal professionals using AI to work smarter, faster, and more accurately.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/sign-up">
              <Button size="lg" variant="secondary" className="text-lg px-8 py-6">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/contact">
              <Button size="lg" variant="outline" className="text-lg px-8 py-6 bg-white/10 hover:bg-white/20 text-white border-white/20">
                Contact Sales
              </Button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-muted/30">
        <div className="container mx-auto px-4 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Scale className="h-6 w-6 text-primary" />
                <span className="font-bold">Indian Legal AI</span>
              </div>
              <p className="text-sm text-muted-foreground">
                AI-powered legal intelligence platform for Indian law.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/features">Features</Link></li>
                <li><Link href="/pricing">Pricing</Link></li>
                <li><Link href="/docs">Documentation</Link></li>
                <li><Link href="/changelog">Changelog</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/about">About Us</Link></li>
                <li><Link href="/blog">Blog</Link></li>
                <li><Link href="/careers">Careers</Link></li>
                <li><Link href="/contact">Contact</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/privacy">Privacy Policy</Link></li>
                <li><Link href="/terms">Terms of Service</Link></li>
                <li><Link href="/disclaimer">Disclaimer</Link></li>
                <li><Link href="/security">Security</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t mt-12 pt-8 text-center text-sm text-muted-foreground">
            <p>© 2024 Indian Legal AI. All rights reserved.</p>
            <p className="mt-2">
              This platform provides informational content and does not constitute legal advice.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
