function _toConsumableArray(e) {
    return _arrayWithoutHoles(e) || _iterableToArray(e) || _nonIterableSpread()
}

function _nonIterableSpread() {
    throw new TypeError("Invalid attempt to spread non-iterable instance")
}

function _iterableToArray(e) {
    if (Symbol.iterator in Object(e) || "[object Arguments]" === Object.prototype.toString.call(e)) return Array.from(e)
}

function _arrayWithoutHoles(e) {
    if (Array.isArray(e)) {
        for (var t = 0, n = new Array(e.length); t < e.length; t++) n[t] = e[t];
        return n
    }
}

function listab(e, t) {
    t = t || 0, $(e + " .tab-title").filter(function(e) {
        return e != t
    }).addClass("tab-off"), $(".tab-content").eq(t).removeClass("none"), $(".tab-content").filter(function(e) {
        return e != t
    }).hide(), $(e + " .tab-title").on("click", function() {
        var t = $(this).data("tab-index");
        $(this).hasClass("tab-off") && ($(e + " .tab-title").addClass("tab-off"), $(this).removeClass("tab-off")), $(".tab-content").hide(), $("#tab-content-" + t).fadeIn("slow")
    })
}

function scrollhide(e) {
    var t, n = 0,
        o = 1;
    $(e).outerHeight();
    $(window).scroll(function(e) {
        t = !0
    }), setInterval(function() {
        t && (! function() {
            var t = $(this).scrollTop();
            if (Math.abs(n - t) <= o) return;
            t >= n ? $(e).hide() : t + $(window).height() < $(document).height() && $(e).show();
            n = t
        }(), t = !1)
    }, 250)
}

function scrollmenuside(e) {
    var t, n = 0,
        o = 1;
    $(e).outerHeight();
    $(window).scroll(function(e) {
        t = !0
    }), setInterval(function() {
        t && (! function() {
            var t = $(this).scrollTop();
            if (Math.abs(n - t) <= o) return;
            t >= n ? ($(e).hide(), $("#mainpart").removeClass("menuside")) : t + $(window).height() < $(document).height() && ($(e).show(), $("#mainpart").addClass("menuside"));
            n = t
        }(), t = !1)
    }, 250)
}

function rdtoggle(e) {
    $(e).click(function() {
        classaffect = $(this).data("affect"), classold = $(".isMoved").data("affect"), $(this).hasClass("isMoved") ? $(classaffect).hide() : ($(classold).hide(), $(".rd_sd-button_item").removeClass("isMoved"), $(classaffect).show()), $(this).toggleClass("isMoved")
    })
}

function getParameterByName(e, t) {
    t || (t = window.location.href), e = e.replace(/[\[\]]/g, "\\$&");
    var n = new RegExp("[?&]" + e + "(=([^&#]*)|&|#|$)").exec(t);
    return n ? n[2] ? decodeURIComponent(n[2].replace(/\+/g, " ")) : "" : null
}
$(document).ajaxError(function(e, t, n, o) {
    var i = "",
        a = t.responseJSON.errors;
    for (var s in a) a.hasOwnProperty(s) && a[s].forEach(function(e) {
        i += e + "\n"
    });
    alert(i)
}), $(document).ready(function() {
    (token = $('meta[name="csrf-token"]').attr("content"), $("#mainpart").css({
        "min-height": window.innerHeight - $("#footer").outerHeight(!0)
    }), $(window).on("resize", function() {
        $("#mainpart").css({
            "min-height": window.innerHeight - $("#footer").outerHeight(!0)
        })
    }), $("main.reading-page").length) || new Headroom(document.querySelector("#navbar")).init();
    $("time.timeago").timeago();
    var e = {
        controls: !1,
        mouseDrag: !0,
        navPosition: "bottom",
        slideBy: "page"
    };
    $(".daily-recent_views .slider").length && tns(Object.assign({
        container: ".daily-recent_views .slider",
        items: 4,
        loop: !1,
        responsive: {
            0: {
                items: 2
            },
            768: {
                items: 3
            },
            980: {
                items: 4
            },
            1200: {
                items: 4
            }
        }
    }, e)), $(".js-finished-series .slider").length && tns(Object.assign({
        container: ".js-finished-series .slider",
        items: 8,
        loop: !1,
        responsive: {
            0: {
                items: 2
            },
            768: {
                items: 4
            },
            980: {
                items: 6
            },
            1200: {
                items: 8
            }
        }
    }, e)), $(".mobile-toggle header").click(function() {
        $(this).parent().find(".summary.at-series").toggle(), $(this).parent().find(".listall_summary.at-volume").toggle(), $(this).parent().find("main").toggle()
    }), $(window).on("scroll", function() {
        $(window).scrollTop() > 50 ? $(".backtoTop").show() : $(".backtoTop").hide()
    }), $(".backtoTop").on("click", function() {
        var e = $(this).data("scrollto");
        $("html, body").animate({
            scrollTop: $(e).offset().top
        })
    }), $("#sidenav-icon, .nav-user_icon, #noti-icon, .nav-has-submenu, #guest-menu").on("click", function(e) {
        e.stopPropagation();
        var t = $(this),
            n = t.find(".hidden-block");
        t.parents(".hidden-block").first().is(":visible") || ($(".active").not(t).removeClass("active"), $(".hidden-block").not(n).addClass("none")), t.toggleClass("active"), n.toggleClass("none")
    }), $(document).on("click", function() {
        $("#navbar .hidden-block").addClass("none"), $("#navbar .active").removeClass("active")
    }), $("div.navbar-search").on("click", function(e) {
        e.stopPropagation()
    }), $(".nightmode-toggle").on("click", function(e) {
        e.stopPropagation(), $(this).find(".toggle-icon").find("i").toggleClass("fa-toggle-off fa-toggle-on"), Cookies.get("night_mode") ? (Cookies.remove("night_mode"), $("#night-mode-css").remove()) : (Cookies.set("night_mode", !0, {
            expires: 365
        }), window.location.reload())
    })
}), $(document).ajaxComplete(function() {
    setTimeout(function() {
        $("time.timeago").timeago()
    }, 1e3)
}), $(document).ready(function() {
    if ("undefined" != typeof chapter_id && chapter_id > 0 && (bookmark_data = {
            _token: token,
            chapter_id: chapter_id,
            line_id: 0
        }, $("#bookmark_top").on("click", function() {
            if ($(this).addClass("on"), !isLoggedIn) return alert("Bạn phải đăng nhập để sử dụng bookmark"), !1;
            var e = $(".reading-content p#" + bookmark_data.line_id).text().trim().substring(0, 30) + "...";
            bookmark_data.line_id > 0 && $.post("/action/chapter/bookmark", bookmark_data, function(t) {
                "success" == t.status ? ($("ul#bookmarks_list").append('<li data-line="' + t.line_id + '"><span class="pos_bookmark">Đoạn thứ ' + t.line_id + '</span><small style="display: block">' + e + '</small><span data-item="' + t.bookmark_id + '" class="del_bookmark remove_bookmark"><i class="fas fa-times"></i></span></li>'), alert("Bạn đã lưu bookmark thành công đoạn thứ " + t.line_id)) : alert(t.message)
            }, "json")
        }), $(window).on("scroll", function() {}), $(".reading-content p").on("click", function() {
            var e = $(this);
            if ($(window).width() > 979) {
                var t = e.offset().top - $("body").offset().top + e.scrollTop(),
                    n = e.offset().left - $(".reading-content").offset().left - $(".save_bookmark").outerWidth(!0);
                $(".save_bookmark").css({
                    height: e.height() + 28 + "px",
                    right: n + "px",
                    top: t + "px",
                    display: ""
                })
            } else $("#bookmark_top").toggleClass("on"), $("#rd-side_icon").toggle();
            bookmark_data.line_id = e.attr("id")
        }), $(".save_bookmark").on("click", function() {
            if (!isLoggedIn) return alert("Bạn phải đăng nhập để sử dụng bookmark"), !1;
            $(window).width() > 979 && bookmark_data.line_id > 0 && $.post("/action/chapter/bookmark", bookmark_data, function(e) {
                "success" == e.status ? ($("ul#bookmarks_list").append('<li data-line="' + e.line_id + '"><span class="pos_bookmark">Đoạn thứ ' + e.line_id + '</span><span data-item="' + e.bookmark_id + '" class="del_bookmark remove_bookmark"><i class="fas fa-times"></i></span></li>'), alert("Bạn đã lưu bookmark thành công đoạn thứ " + e.line_id)) : alert(e.message)
            }, "json")
        }), $("ul#bookmarks_list").on("click", "span.pos_bookmark", function() {
            var e = $("#" + $(this).parent().data("line"));
            $("body,html").animate({
                scrollTop: e.offset().top - $("body").offset().top + e.scrollTop()
            })
        }), $("ul#bookmarks_list").on("click", "span.remove_bookmark", function() {
            _this = $(this), bookmark_id = _this.data("item"), $.post("/action/chapter/removebookmark", {
                _token: token,
                bookmark_id: bookmark_id
            }, function(e) {
                "success" == e.status && _this.parent().fadeOut("normal", function() {
                    $(this).parent("li").remove()
                })
            }, "json")
        }), $(document).keydown(function(e) {
            if ("INPUT" != e.target.nodeName && "TEXTAREA" != e.target.nodeName && 1 != e.target.isContentEditable) {
                var t = e.which || e.keyCode,
                    n = $(".fa-backward").parent().attr("href") || "",
                    o = $(".fa-forward").parent().attr("href") || "";
                switch (t) {
                    case 37:
                        "" != n && (window.location.href = n);
                        break;
                    case 39:
                        "" != o && (window.location.href = o);
                        break;
                    case 27:
                        $(".black-click").click()
                }
            }
        }), Object.keys(readingObject).length)) {
        var e = JSON.parse(localStorage.getItem("reading_series")) || [];
        for (i = 0; i < e.length; i++)
            if (e[i].series_id == series_id) {
                e.splice(i, 1);
                break
            }
        e.unshift(readingObject), e.length > 24 && e.pop(), localStorage.setItem("reading_series", JSON.stringify(e))
    }
}), $(document).ready(function() {
    function e(e) {
        (e.find("img[alt]").length || e.outerHeight() >= 90) && e.next(".comment_see_more").removeClass("none")
    }

    function t() {
        $(".ln-comment-content").each(function() {
            e($(this))
        })
    }
    $(".ln-comment-body").on("click", "span.span-pin", function() {
        $.post("/action/series/pin_comment", {
            _token: token,
            series_id: comment_typeid,
            comment_id: $(this).closest(".ln-comment-item").data("comment")
        }, function(e) {
            "success" == e.status ? window.location.replace(e.url) : alert(e.message)
        })
    }), t(), $(".ln-comment-body").on("click", ".comment_see_more", function(e) {
        var t;
        (t = $(this)).prev().css("max-height", "initial"), t.remove()
    }), $("form.comment_form input.button").on("click", function() {
        var t = tinymce.activeEditor.getContent();
        $.post("/action/comment/new", {
            _token: token,
            type: comment_type,
            type_id: comment_typeid,
            content: t,
            parent_id: 0
        }, function(t) {
            if ("success" == t.status && "" != t.html) {
                var n = $(".ln-comment-body");
                $("html,body").animate({
                    scrollTop: n.offset().top - $("body").offset().top + n.scrollTop()
                }), $("#ln-comment-submit").after($('<div class="ln-comment-group">' + t.html + "</div>").fadeIn(700)), tinymce.activeEditor.setContent(""), e($("#ln-comment-" + t.comment_id).find(".ln-comment-content"))
            } else alert(t.message)
        }, "json")
    }), $(".ln-comment-body").on("click", ".do-reply", function() {
        var e = $(this),
            t = e.closest(".ln-comment-item").data("comment"),
            n = e.closest(".ln-comment-item").data("parent");
        if ($("#ln-comment-" + t).next().find("textarea.comment_reply").length) $(".reply-form").remove();
        else {
            $(".reply-form").remove();
            var o = t != n ? "@" + $("#ln-comment-" + t + " .ln-comment-user_name a").text() + ":&nbsp;" : "";
            $("#ln-comment-" + t).after($('<div class="ln-comment-reply reply-form"><div class="ln-comment-form"><textarea class="comment_reply"></textarea><div class="comment_toolkit clear"><input type="button" class="button submit_reply" value="Trả lời" data-parent="' + n + '"></div></div></div>')), tinymce.init(tinymce.activeEditor.settings), tinymce.activeEditor.setContent(o)
        }
    }), $(".ln-comment-body").on("click", "input.submit_reply", function() {
        var t = tinymce.activeEditor.getContent(),
            n = parseInt($(this).data("parent")) || 0;
        $.post("/action/comment/new", {
            _token: token,
            type: comment_type,
            type_id: comment_typeid,
            content: t,
            parent_id: n
        }, function(t) {
            if ("success" == t.status && "" != t.html) {
                $("#ln-comment-" + n).parent().append($('<div class="ln-comment-reply">' + t.html + "</div>"));
                var o = $("#ln-comment-" + t.comment_id);
                $("html,body").animate({
                    scrollTop: o.offset().top - $("body").offset().top + o.scrollTop() - 270
                }), e(o.find(".ln-comment-content"))
            } else alert(t.message);
            $(".reply-form").remove()
        }, "json")
    }), $(".ln-comment-body").on("click", ".span-edit", function() {
        var e = $(this).closest(".ln-comment-item").data("comment"),
            t = $("#ln-comment-" + e),
            n = t.find(".ln-comment-content");
        if (t.find(".ln-comment-content .comment_hidden").length && n.html(t.find(".ln-comment-content .comment_hidden").html()), t.find(".ln-comment-form").length) return t.find(".ln-comment-form").remove(), void n.show();
        $(".edit-form").remove(), n.css("max-height", "initial"), n.next(".comment_see_more").remove(), n.after('<div class="ln-comment-form edit-form" style="padding-left: 10px"><textarea class="comment_edit"></textarea><div class="comment_toolkit clear"><input type="button" class="button submit_edit" value="Sửa" data-comment="' + e + '"></div></div>'), n.hide(), tinymce.init(tinymce.activeEditor.settings), tinymce.activeEditor.setContent(n.html())
    }), $(".ln-comment-body").on("click", "input.submit_edit", function() {
        var e = parseInt($(this).data("comment")) || 0,
            t = tinymce.activeEditor.getContent();
        $.post("/action/comment/update", {
            _token: token,
            comment_id: e,
            content: t
        }, function(t) {
            var n = $("#ln-comment-" + e);
            "success" == t.status && "" != t.html ? ($("html,body").animate({
                scrollTop: n.offset().top - $("body").offset().top + n.scrollTop()
            }), n.find(".ln-comment-content").html(t.html).show()) : (n.find(".ln-comment-content").show(), alert(t.message)), $(".edit-form").remove()
        }, "json")
    }), $(".ln-comment-body").on("click", ".span-delete", function() {
        var e = $(this),
            t = parseInt(e.closest(".ln-comment-item").data("comment"));
        if (!confirm("Bạn có muốn xóa bình luận?")) return !1;
        $.post("/action/comment/delete", {
            _token: token,
            comment_id: t
        }, function(e) {
            if ("success" == e.status) {
                var n = $("#ln-comment-" + t);
                n.find(".ln-comment-content").html("(Bình luận đã bị xóa)"), n.find("hr.ln-comment").remove(), n.find(".ln-comment-toolkit").remove()
            } else alert(e.message)
        })
    }), $(".ln-comment-body").on("click", ".paging_item, #refresh_comment", function(e) {
        e.preventDefault();
        var n = $(this);
        "refresh_comment" == n.attr("id") && n.addClass("refresher");
        var o = getParameterByName("page", n.attr("href")) || 1;
        return $.post("/comment/ajax_paging", {
            _token: token,
            type: comment_type,
            type_id: comment_typeid,
            page: o
        }, function(e) {
            if ("success" == e.status && "" != e.html) {
                $(".ln-comment-body").find(".ln-comment-group, .ln-comment-page").remove(), $(".ln-comment-body").append(e.html);
                var o = $(".ln-comment-body").parent();
                t(), $("html,body").animate({
                    scrollTop: o.offset().top - $("body").offset().top + o.scrollTop()
                })
            } else alert(e.message);
            n.removeClass("refresher")
        }, "json"), !1
    }), $(".ln-comment-body").on("click", ".fetch_reply", function(e) {
        var n = $(this);
        n.next().show(), $.post("/comment/fetch_reply", {
            _token: token,
            parent_id: n.data("parent"),
            offset: n.parent().find(".ln-comment-item").length,
            after: n.parent().find(".ln-comment-item").last().data("comment")
        }, function(e) {
            "success" == e.status && "" != e.html ? (n.next().hide(), e.remaining > 0 ? n.text(e.fetchReplyText) : n.hide(), n.before(e.html), t()) : "error" == e.status && alert(e.message)
        }, "json")
    })
}), "undefined" != typeof series_id && series_id > 0 && (-1 == (Cookies.getJSON("mature_confirm") || []).indexOf(series_id) && $("#mature_modal").css("display", "block"), $("button#mature_confirm").on("click", function(e) {
    var t = Cookies.getJSON("mature_confirm") || []; - 1 == t.indexOf(series_id) && (t.push(series_id), Cookies.set("mature_confirm", t, {
        expires: 3
    })), $("#mature_modal").css("display", "none")
})), $(document).ready(function() {
    if ("1" == $('meta[name="logged-in"]').attr("content") && !$("main.reading-page").length) {
        var e = function(e) {
                e.notification_count > 0 ? ($("#noti-icon").find(".noti-unread").remove(), $("#noti-icon .icon-wrapper").append('<span class="noti-unread">' + e.notification_count + "</span>"), $("#noti-icon #noti-sidebar").find("#noti-content").prepend(e.html)) : $("#noti-icon").find(".noti-unread").remove(), e.seriesunread_count > 0 ? ($("#series-unread-icon").find(".noti-unread").remove(), $("#series-unread-icon .icon-wrapper").append('<span class="noti-unread">' + e.seriesunread_count + "</span>")) : $("#series-unread-icon").find(".noti-unread").remove(), e.pmunread_count > 0 ? ($(".at-user_avatar").addClass("icon-notify"), $(".at-user_list").addClass("icon-notify")) : ($(".at-user_avatar").removeClass("icon-notify"), $(".at-user_list").removeClass("icon-notify")), o = parseInt(e.total), t(o > 0 ? "(" + o + ") " + n : n)
            },
            t = function(e) {
                document.title = e
            },
            n = document.title,
            o = 0;
        $("span.noti-unread").each(function() {
                o += parseInt($(this).text())
            }), o > 0 && (document.title = "(" + o + ") " + document.title), $("#noti-icon").on("click", function(e) {
                e.stopPropagation();
                $(this).find(".noti-sidebar");
                var t = $(this).find("span.noti-unread");
                "" != t.text().trim() && $.post("/action/notification/clearunread", {
                    _token: token
                }, function(e) {
                    "success" == e.status ? (t.remove(), o = 0, $("span.noti-unread").each(function() {
                        o += parseInt($(this).text())
                    }), document.title = o > 0 ? "(" + o + ") " + n : n) : alert(e.message)
                }, "json")
            }), $(".noti-sidebar").on("click", function(e) {
                e.stopPropagation()
            }), $(document).on("click", function() {
                var e = $(".noti-sidebar");
                e.hasClass("block") && e.toggleClass("none block")
            }), $("#noti-icon #noti-sidebar").on("mousedown", ".noti-item", function() {
                var e = $(this);
                e.hasClass("untouch") && $.post("/action/notification/touch", {
                    _token: token,
                    notification_id: $(this).data("notification")
                }, function(t) {
                    "success" == t.status || "touched" == t.status ? e.removeClass("untouch") : alert(t.message)
                }, "json")
            }),
            function t() {
                setTimeout(function() {
                    var n = $(".noti-item time.timeago").first().attr("title") || "";
                    ((new Date).getTime() / 1e3 | 0) - (localStorage.getItem("ln_refresh_time") || 0) < 180 ? t() : (localStorage.setItem("ln_refresh_time", (new Date).getTime() / 1e3 | 0), $.post("/action/notification/fresh", {
                        last: n
                    }, function(n) {
                        "success" == n.status && (e(n), localStorage.setItem("ln_crosstab", JSON.stringify(n))), t()
                    }, "json"))
                }, 18e4)
            }(), $(window).on("storage", function(t) {
                "ln_crosstab" == t.originalEvent.key && e(JSON.parse(localStorage.getItem("ln_crosstab")))
            })
    }
}), $(document).ready(function() {
    $(".spoiler_toggle").on("click", function(e) {
        e.preventDefault();
        var t, n = $(this);
        return (t = n.parent().next()).is(":visible") ? (t.hide(), n.text("Click vào để hiển thị nội dung")) : (t.show(), n.text("Click vào để ẩn nội dung")), !1
    })
}), $(document).ready(function() {
    "undefined" != typeof series_id && series_id > 0 && $("span.star-evaluate-item").on("click", function() {
        if ("1" == $('meta[name="logged-in"]').attr("content")) {
            var e = $(this).data("value");
            $.post("/action/series/updaterating", {
                _token: $('meta[name="csrf-token"]').attr("content"),
                series_id: series_id,
                value: e
            }, function(e) {
                "success" == e.status ? alert("Cảm ơn bạn đã đánh giá truyện") : e.message ? alert(e.message) : alert("Error")
            }, "json")
        } else alert("Bạn phải đăng nhập để đánh giá truyện")
    })
}), $(document).ready(function() {
    if ($("main.search-page div.search-advance").length) {
        var e = new Set,
            t = new Set;
        $(".search-advance_toggle").on("click", function() {
            $(".search-advance").toggle(), $(this).toggleClass("on")
        }), $(".genre_label").on("click", function() {
            var e = $(this);
            e.data("genre-id");
            1 == e.find("i.fa-square").length ? e.find("i.far").toggleClass("far fas fa-square fa-check") : 1 == e.find("i.fa-check").length ? e.find("i.fas").toggleClass("fa-check fa-times") : e.find("i.fas").toggleClass("far fas fa-times fa-square")
        }), $("form").on("submit", function(n) {
            n.preventDefault(), $(".gerne-icon i").each(function(n, o) {
                var i = $(this),
                    a = i.parents("label").data("genre-id");
                i.hasClass("fa-check") ? e.add(a) : i.hasClass("fa-times") && t.add(a)
            });
            var o = "?selectgenres=" + _toConsumableArray(e).join(",") + "&rejectgenres=" + _toConsumableArray(t).join(",");
            o += "&" + $(this).serialize(), window.location.href = window.location.href.split("?")[0] + o
        })
    }
}), $(document).ready(function() {
    $(".container").width() <= 768 && $(".gradual-mobile").find("main").hide(), $(".gradual-mobile header").on("click", function() {
        var e = $(this).parent();
        e.find(".see_more").click(), e.find("main").toggle(), $(this).find(".mobile-icon i").toggleClass("fa-chevron-down fa-chevron-up")
    }), $("#collect").on("click", function(e) {
        $.post("/action/series/collect", {
            _token: token,
            series_id: series_id
        }, function(e) {
            var t = $("#collect");
            "success" == e.status ? (e.collected ? alert("Bạn đã theo dõi truyện.") : alert("Bạn đã ngừng theo dõi truyện."), t.toggleClass("follow followed"), t.find("i").toggleClass("far fas")) : ($(".summary-content").css({
                maxHeight: "150px",
                overflow: "hidden"
            }), _this.html('<i class="fa fa-angle-double-down" aria-hidden="true"></i> Xem thêm'))
        }, "json")
    }), $(".feature-section .summary-content").outerHeight() >= 100 && $(".feature-section .summary-more").removeClass("none"), $(".mobile-more").click(function(e) {
        e.preventDefault(), $(this).parent().find("li").removeClass("none"), $(this).remove()
    }), $(".summary-more").click(function(e) {
        e.preventDefault();
        var t = $(this),
            n = $(this).find(".see_more");
        return t.hasClass("more-state") ? ($(".feature-section .summary-content").css({
            maxHeight: "none",
            overflow: ""
        }), n.html("Ẩn đi")) : ($(".feature-section .summary-content").css({
            maxHeight: "100px",
            overflow: "hidden"
        }), n.html("Xem thêm")), t.toggleClass("more-state less-state"), !1
    })
});