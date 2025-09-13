$(document).ready(function() {
  'use strict';

  var menuOpenIcon = $(".nav__icon-menu"),
    menuCloseIcon = $(".nav__icon-close"),
    menuList = $(".menu-overlay"),
    searchOpenIcon = $(".search-button"),
    searchCloseIcon = $(".search__close"),
    searchInput = $(".search__text"),
    searchBox = $(".search");


  /* =======================
  // Menu and Search
  ======================= */
  menuOpenIcon.click(function () {
    menuOpen();
  })

  menuCloseIcon.click(function () {
    menuClose();
  })

  searchOpenIcon.click(function () {
    searchOpen();
  });

  searchCloseIcon.click(function () {
    searchClose();
  });

  function menuOpen() {
    menuList.addClass("is-open");
  }

  function menuClose() {
    menuList.removeClass("is-open");
  }

  function searchOpen() {
    searchBox.addClass("is-visible");
    setTimeout(function () {
      searchInput.focus();
      // 검색창이 열릴 때 이전 결과 클리어
      $("#js-results-container").empty();
    }, 300);
  }

  function searchClose() {
    searchBox.removeClass("is-visible");
  }

  $('.search, .search__box').on('click keyup', function (event) {
    if (event.target == this || event.keyCode == 27) {
      $('.search').removeClass('is-visible');
    }
  });


  /* =======================
  // Animation Load Page
  ======================= */
  setTimeout(function(){
    $('body').addClass('is-in');
  },150)


  /* =======================
  // Typing Animation for Hero Title
  ======================= */
  function initTypeAnimation() {
    const typeElement = document.querySelector('.hero__title[data-type-text]');
    if (!typeElement) return;

    const texts = typeElement.getAttribute('data-type-text').split('|');
    const typingSpeed = parseInt(typeElement.getAttribute('data-type-speed')) || 100;
    const deletingSpeed = parseInt(typeElement.getAttribute('data-delete-speed')) || 50;
    const pauseDuration = parseInt(typeElement.getAttribute('data-pause-duration')) || 2000;
    
    let textIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let isPaused = false;

    // 초기 텍스트 설정
    typeElement.innerHTML = '';

    function typeText() {
      if (isPaused) {
        setTimeout(typeText, pauseDuration);
        isPaused = false;
        return;
      }

      const currentText = texts[textIndex];
      
      if (isDeleting) {
        // 텍스트 삭제
        typeElement.innerHTML = currentText.substring(0, charIndex - 1) + '<span class="typing-cursor">|</span>';
        charIndex--;
        
        if (charIndex === 0) {
          isDeleting = false;
          textIndex = (textIndex + 1) % texts.length;
          setTimeout(typeText, 500); // 삭제 완료 후 잠시 대기
          return;
        }
        
        setTimeout(typeText, deletingSpeed);
      } else {
        // 텍스트 타이핑
        typeElement.innerHTML = currentText.substring(0, charIndex + 1) + '<span class="typing-cursor">|</span>';
        charIndex++;
        
        if (charIndex === currentText.length) {
          if (texts.length > 1) {
            // 여러 텍스트가 있으면 삭제 모드로 전환
            isPaused = true;
            isDeleting = true;
          } else {
            // 단일 텍스트면 커서만 깜빡임
            typeElement.innerHTML = currentText + '<span class="typing-cursor">|</span>';
            return;
          }
        }
        
        setTimeout(typeText, typingSpeed);
      }
    }

    // 타이핑 시작
    setTimeout(typeText, 1000); // 페이지 로드 후 1초 대기
  }

  // 타이핑 애니메이션 초기화
  initTypeAnimation();


  /* =======================
  // Glitch Text Animation for Logo
  ======================= */
  function initGlitchLogo() {
    const logoLink = document.querySelector('.logo__link.glitch-text');
    if (!logoLink) return;

    // data-text 속성이 이미 설정되어 있는지 확인
    if (logoLink.hasAttribute('data-text')) {
      console.log('Glitch logo animation enabled via config');
      return;
    }

    // 로고 텍스트 가져오기 (fallback)
    const logoText = logoLink.textContent.trim();
    logoLink.setAttribute('data-text', logoText);
    
    console.log('Glitch logo animation initialized for:', logoText);
  }

  // 글리치 로고 애니메이션 초기화
  initGlitchLogo();




  // =====================
  // Simple Jekyll Search v1.10.0 with Enhanced UX
  // =====================
  var searchInstance;
  var searchTimeout;
  
  try {
    searchInstance = SimpleJekyllSearch({
      searchInput: document.getElementById("js-search-input"),
      resultsContainer: document.getElementById("js-results-container"),
      json: "/search.json",
      searchResultTemplate: '{article}',
      noResultsText: '<div class="no-results"><div class="col col-12"><div class="no-results__content"><h3>검색 결과가 없습니다</h3><p>다른 키워드로 다시 시도해보세요.</p></div></div></div>',
      limit: 10,
      fuzzy: false,
      debounceTime: 300,
      exclude: ['date', 'author'],
      success: function() {
        console.log("검색 기능이 성공적으로 초기화되었습니다.");
        
        // 검색 입력 이벤트 리스너 추가
        var searchInput = document.getElementById("js-search-input");
        var resultsContainer = document.getElementById("js-results-container");
        
        if (searchInput && resultsContainer) {
          searchInput.addEventListener('input', function(e) {
            var query = e.target.value.trim();
            
            // 기존 타이머 클리어
            clearTimeout(searchTimeout);
            
            if (query.length === 0) {
              resultsContainer.innerHTML = '';
              return;
            }
            
            if (query.length < 2) {
              resultsContainer.innerHTML = '<div class="search-hint"><div class="col col-12"><p style="text-align: center; color: rgba(238, 238, 238, 0.6); padding: 20px;">최소 2글자 이상 입력해주세요</p></div></div>';
              return;
            }
            
            // 로딩 상태 표시
            resultsContainer.innerHTML = '<div class="search-loading"><div class="col col-12">검색 중...</div></div>';
            
            // 검색 실행 (debounce 적용)
            searchTimeout = setTimeout(function() {
              searchInstance.search(query);
            }, 250);
          });
          
          // 검색창 포커스 시 플레이스홀더 개선
          searchInput.addEventListener('focus', function() {
            this.placeholder = '포스트 제목, 내용, 태그로 검색...';
          });
          
          searchInput.addEventListener('blur', function() {
            this.placeholder = 'Type to search...';
          });
        }
      },
      sortMiddleware: function(a, b) {
        // 제목 매치를 우선순위로 정렬
        var aTitle = a.title.toLowerCase();
        var bTitle = b.title.toLowerCase();
        var query = (a.query || b.query || '').toLowerCase();
        
        var aTitleMatch = aTitle.indexOf(query) !== -1;
        var bTitleMatch = bTitle.indexOf(query) !== -1;
        
        if (aTitleMatch && !bTitleMatch) return -1;
        if (!aTitleMatch && bTitleMatch) return 1;
        
        // 최신 글 우선
        return new Date(b.date) - new Date(a.date);
      }
    });
  } catch (error) {
    console.error("검색 기능 초기화 실패:", error);
    // 검색 입력 필드에 에러 메시지 표시
    var searchInput = document.getElementById("js-search-input");
    if (searchInput) {
      searchInput.placeholder = "검색 기능을 사용할 수 없습니다";
      searchInput.disabled = true;
    }
  }


  /* =======================
  // LazyLoad Images
  ======================= */
  var lazyLoadInstance = new LazyLoad({
    elements_selector: '.lazy'
  })


  // =====================
  // Ajax Load More
  // =====================
  var $load_posts_button = $('.load-more-posts');

  $load_posts_button.click(function(e) {
    e.preventDefault();
    var loadMore = $('.load-more-section');
    var request_next_link = pagination_next_url.split('/page')[0] + '/page/' + pagination_next_page_number + '/';

    $.ajax({
      url: request_next_link,
      beforeSend: function() {
        $load_posts_button.text('Loading...');
      }
    }).done(function(data) {
      var posts = $('.grid__post', data);
      $('.grid').append(posts);

      var lazyLoadInstance = new LazyLoad({
        elements_selector: '.lazy'
      })

      $load_posts_button.text('Load more');
      pagination_next_page_number++;

      if (pagination_next_page_number > pagination_available_pages_number) {
        loadMore.addClass('hide');
      }
    });
  });


  /* =======================
  // Responsive Videos
  ======================= */
  $(".post__content, .page__content").fitVids({
    customSelector: ['iframe[src*="ted.com"]', 'iframe[src*="player.twitch.tv"]', 'iframe[src*="facebook.com"]']
  });


  /* =======================
  // Zoom Image
  ======================= */
  $(".page img, .post img").attr("data-action", "zoom");
  $(".page a img, .post a img").removeAttr("data-action", "zoom");


  /* =======================
  // Scroll Top Button
  ======================= */
  $(".top").click(function() {
    $("html, body")
      .stop()
      .animate({ scrollTop: 0 }, "slow", "swing");
  });
  $(window).scroll(function() {
    if ($(this).scrollTop() > $(window).height()) {
      $(".top").addClass("is-active");
    } else {
      $(".top").removeClass("is-active");
    }
  });

});