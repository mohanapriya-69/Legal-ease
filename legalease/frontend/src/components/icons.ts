/**
 * Maps the `icon` string on each template (served by the backend) to a Lucide
 * component. Adding a new template only requires a matching entry here.
 */

import {
  Briefcase,
  Building2,
  Compass,
  FileSignature,
  FileText,
  GraduationCap,
  Handshake,
  Home,
  KeyRound,
  Landmark,
  MailOpen,
  PenTool,
  ScrollText,
  Shield,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  Truck,
  UserRound,
  UsersRound,
  type LucideIcon,
} from 'lucide-react'

export const TEMPLATE_ICONS: Record<string, LucideIcon> = {
  'shield-check': ShieldCheck,
  briefcase: Briefcase,
  'mail-open': MailOpen,
  'pen-tool': PenTool,
  handshake: Handshake,
  home: Home,
  'key-round': KeyRound,
  'users-round': UsersRound,
  'building-2': Building2,
  compass: Compass,
  truck: Truck,
  'file-signature': FileSignature,
  'scroll-text': ScrollText,
  shield: Shield,
  landmark: Landmark,
  'shopping-bag': ShoppingBag,
  'graduation-cap': GraduationCap,
  sparkles: Sparkles,
  'file-text': FileText,
  'user-round': UserRound,
}

export function templateIcon(name: string): LucideIcon {
  return TEMPLATE_ICONS[name] ?? FileText
}
