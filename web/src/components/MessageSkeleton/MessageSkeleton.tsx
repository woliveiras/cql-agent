import {
  SkeletonAvatar,
  SkeletonBubble,
  SkeletonContainer,
  SkeletonContent,
  SkeletonLine,
} from './MessageSkeleton.styles';

export function MessageSkeleton() {
  return (
    <SkeletonContainer>
      <SkeletonAvatar />
      <SkeletonContent>
        <SkeletonBubble>
          <SkeletonLine width="90%" />
          <SkeletonLine width="75%" />
          <SkeletonLine width="80%" />
        </SkeletonBubble>
      </SkeletonContent>
    </SkeletonContainer>
  );
}
