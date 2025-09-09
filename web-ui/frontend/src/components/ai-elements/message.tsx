import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import type { UIMessage } from 'ai';
import type { ComponentProps, HTMLAttributes } from 'react';

export type MessageProps = HTMLAttributes<HTMLDivElement> & {
  from: UIMessage['role'];
};

export const Message = ({ className, from, ...props }: MessageProps) => (
  <div
    className={cn(
      'group flex w-full items-start gap-3 py-3 min-w-0',
      // Both user and AI messages are left-aligned like Claude Desktop
      from === 'user' ? 'is-user' : 'is-assistant',
      className
    )}
    data-role={from}
    {...props}
  />
);

export type MessageContentProps = HTMLAttributes<HTMLDivElement> & {
  role?: 'user' | 'assistant';
};

export const MessageContent = ({
  children,
  className,
  role,
  ...props
}: MessageContentProps) => {
  const isUser = role === 'user'
  
  return (
    <div
      className={cn(
        'flex flex-col gap-2 text-sm leading-relaxed text-foreground flex-1 min-w-0 overflow-hidden',
        // User messages: dark bubble with rounded corners like Claude
        isUser && 'bg-secondary text-secondary-foreground rounded-2xl px-4 py-3 max-w-[75%]',
        // AI messages: plain text, no background, like Claude Desktop
        !isUser && 'bg-transparent px-0 py-1',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export type MessageAvatarProps = ComponentProps<typeof Avatar> & {
  src: string;
  name?: string;
};

export const MessageAvatar = ({
  src,
  name,
  className,
  ...props
}: MessageAvatarProps) => (
  <Avatar className={cn('size-6 flex-shrink-0', className)} {...props}>
    <AvatarImage alt="" className="mt-0 mb-0" src={src} />
    <AvatarFallback className="text-xs">{name?.slice(0, 2) || 'ME'}</AvatarFallback>
  </Avatar>
);
